from __future__ import absolute_import, print_function
import sys
import json
import os
import pandas as pd
import numpy as np

FUNCTION_NAME_CLASSIFICATION = 'classification'
FUNCTION_NAME_REGRESSION = 'regression'
FUNCTION_NAME_CLUSTERING = 'clustering'
FUNCTION_NAME_UNKNOWN = 'unknown'

SUPPORTED_FUNCTION_NAMES = (
    FUNCTION_NAME_CLASSIFICATION, FUNCTION_NAME_REGRESSION, FUNCTION_NAME_CLUSTERING)


class BaseModel(object):
    def __init__(self, model):
        self.model = model

    def is_support(self):
        raise NotImplementedError()

    def model_type(self):
        raise NotImplementedError()

    def model_version(self):
        raise NotImplementedError()

    def mining_function(self, y_test):
        return FUNCTION_NAME_UNKNOWN

    def serialization(self):
        raise NotImplementedError()

    def runtime(self):
        return 'Python{major}{minor}'.format(major=sys.version_info[0], minor=sys.version_info[1])

    def algorithm(self):
        return self.model.__class__.__name__

    def evaluate_metrics(self, x_test, y_test, data_test, input_function_name):
        raise NotImplementedError()

    def predictors(self, x_test, data_test):
        if x_test is None:
            return []

        result = []
        if isinstance(x_test, np.ndarray) and x_test.ndim <= 2:
            x_test = pd.DataFrame(x_test)
            x_test.columns = ['x' + str(i)
                              for i in range(0, len(x_test.columns))]

        x_test = self._series_to_dataframe(x_test)
        if isinstance(x_test, pd.DataFrame):
            row = json.loads(x_test.iloc[0].to_json())
            cols = row.keys()
            for x in cols:
                result.append({
                    'name': x,
                    'sample': row[x],
                    'type': type(row[x]).__name__
                })
        else:  # numpy array with multiple dimensions than two
            row = x_test[0]
            result.append({
                'name': 'tensor_input',
                'sample': row.tolist(),
                'type': x_test.dtype.name,
                'shape': self._normalize_np_shape(x_test.shape)
            })

        return result

    def targets(self, y_test, data_test):
        if y_test is None:
            return []

        result = []
        if isinstance(y_test, np.ndarray) and y_test.ndim <= 2:
            y_test = pd.DataFrame(y_test)
            y_test.columns = ['y' + str(i)
                              for i in range(0, len(y_test.columns))]

        y_test = self._series_to_dataframe(y_test)
        if isinstance(y_test, pd.DataFrame):
            row = json.loads(y_test.iloc[0].to_json())
            cols = row.keys()
            for x in cols:
                result.append({
                    'name': x,
                    'sample': row[x],
                    'type': type(row[x]).__name__
                })
        else:  # numpy array with multiple dimensions than two
            row = y_test[0]
            result.append({
                'name': 'tensor_target',
                'sample': row.tolist(),
                'type': y_test.dtype.name,
                'shape': self._normalize_np_shape(y_test.shape)
            })

        return result

    def outputs(self, y_test, data_test, **kwargs):
        return []

    @staticmethod
    def extract_major_minor_version(version):
        result = version
        elements = version.split('.')
        if len(elements) > 2:
            result = '{major}.{minor}'.format(
                major=elements[0], minor=elements[1])
        return result

    @staticmethod
    def evaluate_metrics_by_sklearn(wrapped_model, x_test, y_test, input_function_name):
        if x_test is None or y_test is None:
            return {}

        try:
            function_name = input_function_name if input_function_name else wrapped_model.mining_function(
                y_test)
            if function_name == FUNCTION_NAME_CLASSIFICATION:
                from sklearn.metrics import accuracy_score
                y_pred = wrapped_model.model.predict(x_test)
                accuracy = accuracy_score(y_test, y_pred)
                return {
                    'accuracy': accuracy
                }
            elif function_name == FUNCTION_NAME_REGRESSION:
                from sklearn.metrics import explained_variance_score
                y_pred = wrapped_model.model.predict(x_test)
                explained_variance = explained_variance_score(y_test, y_pred)
                return {
                    'explainedVariance': explained_variance
                }
            else:
                return {}
        except:
            return {}

    @staticmethod
    def _normalize_np_shape(shape):
        result = None
        if shape is not None and len(shape) > 1:
            result = []
            for idx, d in enumerate(shape):
                if idx == 0:
                    result.append(None)
                else:
                    result.append(d)
        return result

    @staticmethod
    def _series_to_dataframe(data):
        if isinstance(data, pd.Series):
            return pd.DataFrame(data)
        return data

    def _test_data_to_ndarray(self, x_y_test, data_test):
        data = self._to_dataframe(x_y_test, data_test)
        if isinstance(data, pd.DataFrame):
            return data.values
        return data

    @staticmethod
    def _to_ndarray(data):
        return data.values if isinstance(data, (pd.DataFrame, pd.Series)) else data

    @staticmethod
    def _to_dataframe(x_y_test, data_test):
        if x_y_test is None and data_test is not None:
            x_y_test = data_test.limit(1).toPandas()
        if isinstance(x_y_test, pd.Series):
            x_y_test = pd.DataFrame(x_y_test)
        return x_y_test

    def _infer_mining_function(self, y_test):
        if y_test is None:
            return FUNCTION_NAME_UNKNOWN

        y_test = self._to_ndarray(y_test)
        if y_test.ndim >= 2:
            return FUNCTION_NAME_CLASSIFICATION if y_test.shape[y_test.ndim - 1] > 1 else FUNCTION_NAME_REGRESSION

        # float numbers are treated as a regression problem
        return FUNCTION_NAME_REGRESSION if y_test.dtype.kind in 'fc' else FUNCTION_NAME_CLASSIFICATION

    @staticmethod
    def _compatible_shape(shape1, shape2):
        # could be tuple and list
        shape1 = list(shape1)
        shape2 = list(shape2)
        if len(shape1) > 1:
            shape1 = shape1[1:]
        if len(shape2) > 1:
            shape2 = shape2[1:]
        return BaseModel._element_count(shape1) == BaseModel._element_count(shape2)

    @staticmethod
    def _element_count(shape):
        result = 1
        for n in shape:
            if isinstance(n, int):
                result *= n
        return result


class CustomModel(BaseModel):
    def __init__(self, model):
        BaseModel.__init__(self, model)

    def is_support(self):
        return not isinstance(self.model, (str, bytes, bytearray))

    def model_type(self):
        return 'Custom'

    def model_version(self):
        return 'unknown'

    def serialization(self):
        return 'pickle'

    def evaluate_metrics(self, x_test, y_test, data_test, input_function_name):
        return {}


class ONNXModel(BaseModel):
    def __init__(self, model):
        super(ONNXModel, self).__init__(model)
        self.onnx_model = None
        self.sess = None
        self._algorithm = None

    def is_support(self):
        try:
            import onnx

            if isinstance(self.model, onnx.ModelProto):
                self.onnx_model = self.model
                return True

            if isinstance(self.model, (bytes, bytearray)):
                onnx_model = onnx.load_model_from_string(self.model)
            else:
                # could be either readable or a file path
                onnx_model = onnx.load_model(self.model)

            onnx.checker.check_model(onnx_model)
            self.onnx_model = onnx_model
            return True
        except Exception:
            return False

    def model_type(self):
        return 'ONNX'

    def model_version(self):
        return None

    def mining_function(self, y_test):
        algorithm = self.algorithm()
        if algorithm is not None:
            if algorithm in ('LinearClassifier', 'SVMClassifier', 'TreeEnsembleClassifier'):
                return FUNCTION_NAME_CLASSIFICATION
            if algorithm in ('LinearRegressor', 'SVMRegressor', 'TreeEnsembleRegressor'):
                return FUNCTION_NAME_REGRESSION
        return self._infer_mining_function(y_test)

    def serialization(self):
        return 'onnx'

    def runtime(self):
        return 'ONNX Runtime'

    def algorithm(self):
        if self._algorithm is None:
            use_onnx_ml = False
            if self.onnx_model is not None:
                graph = self.onnx_model.graph
                for node in graph.node:
                    if node.domain == 'ai.onnx.ml':
                        use_onnx_ml = True
                        if node.op_type in ('LinearClassifier', 'LinearRegressor', 'SVMClassifier', 'SVMRegressor',
                                            'TreeEnsembleClassifier', 'TreeEnsembleRegressor'):
                            self._algorithm = node.op_type
                            break
                if self._algorithm is None and not use_onnx_ml:
                    self._algorithm = 'NeuralNetwork'
        return self._algorithm

    def quick_prediction(self, x_test, input_function_name):
        if x_test is None:
            return {}

        try:
            result = {}
            function_name = input_function_name if input_function_name else self.mining_function(
                None)
            # convert to numpy array if not
            x_test = self._to_ndarray(x_test)
            sess = self._get_inference_session()
            y_pred = None
            if function_name in (FUNCTION_NAME_CLASSIFICATION, FUNCTION_NAME_REGRESSION) and len(
                    sess.get_inputs()) == 1:
                input_name = sess.get_inputs()[0].name
                output = sess.run(None, {
                                  input_name: x_test.astype(np.float32)})
                y_pred = np.asarray(output[0])
                shape = y_pred.shape
                if len(shape) > 1 and shape[1] > 1:
                    y_pred = np.argmax(y_pred, axis=1)
                result["predicted_species"] = y_pred[0]
                probabilities = output[1][0]
                for i in range(len(probabilities)):
                    result["probability_{}".format(i)] = probabilities[i]
                return {
                    "result": [result],
                }

        except Exception as e:
            import traceback
            traceback.print_exc()

    def evaluate_metrics(self, x_test, y_test, data_test, input_function_name):
        if x_test is None or y_test is None:
            return {}

        try:
            function_name = input_function_name if input_function_name else self.mining_function(
                y_test)

            # convert to numpy array if not
            x_test = self._to_ndarray(x_test)
            y_test = self._to_ndarray(y_test)

            shape = y_test.shape
            if len(shape) > 1 and shape[1] > 1:
                y_test = np.argmax(y_test, axis=1)

            sess = self._get_inference_session()
            y_pred = None
            if function_name in (FUNCTION_NAME_CLASSIFICATION, FUNCTION_NAME_REGRESSION) and len(
                    sess.get_inputs()) == 1:
                input_name = sess.get_inputs()[0].name
                y_pred = sess.run([sess.get_outputs()[0].name], {
                                  input_name: x_test.astype(np.float32)})[0]
                y_pred = np.asarray(y_pred)
                shape = y_pred.shape
                if len(shape) > 1 and shape[1] > 1:
                    y_pred = np.argmax(y_pred, axis=1)

            if y_pred is not None:
                if function_name == FUNCTION_NAME_CLASSIFICATION:
                    from sklearn.metrics import accuracy_score
                    accuracy = accuracy_score(y_test, y_pred)
                    return {
                        'accuracy': accuracy
                    }
                elif function_name == FUNCTION_NAME_REGRESSION:
                    from sklearn.metrics import explained_variance_score
                    explained_variance = explained_variance_score(
                        y_test, y_pred)
                    return {
                        'explainedVariance': explained_variance
                    }
            else:
                return {}
        except Exception as e:
            return {}

    def predictors(self, x_test, data_test):
        result = []

        sess = self._get_inference_session()
        for x in sess.get_inputs():
            result.append({
                'name': x.name,
                'type': x.type,
                'shape': x.shape
            })

        # suppose there is only 1 tensor input
        data = self._test_data_to_ndarray(x_test, data_test)
        if data is not None and len(result) == 1:
            if self._compatible_shape(data.shape, result[0]['shape']):
                result[0]['sample'] = [data[0].tolist()]
        return result

    def targets(self, y_test, data_test):
        return []

    def outputs(self, y_test, data_test, **kwargs):
        result = []

        sess = self._get_inference_session()
        for x in sess.get_outputs():
            result.append({
                'name': x.name,
                'type': x.type,
                'shape': x.shape
            })
        return result

    def _get_inference_session(self):
        if self.sess is None:
            import onnxruntime as rt
            self.sess = rt.InferenceSession(
                self.onnx_model.SerializeToString())
        return self.sess


def get_model_info(path, type):
    if type == "onnx":
        model = ONNXModel(path)
    else:
        return {
            "stderr": "Not implemented model type."
        }
    response = {}
    if model.is_support():
        response['input'] = model.predictors(None, None)
        response['output'] = model.outputs(None, None)
        response['model_type'] = model.model_type()
        response['algorithm'] = model.algorithm(
        ) + "(" + model.mining_function(None) + ")"
        response['engine'] = model.runtime()
        return response
    else:
        return {
            "stderr": "Not supported."
        }


def quick_predict(path, type, x_test):
    if type == "onnx":
        model = ONNXModel(path)
    else:
        return {
            "stderr": "Not implemented model type."
        }
    if model.is_support():
        return model.quick_prediction(x_test, None)
    else:
        return {
            "stderr": "Not supported."
        }


if __name__ == "__main__":
    info = get_model_info(
        "D:\Program\Github\ML-Platform\Backend\ml\logreg_iris.onnx", "onnx")
    print(info)
    x_test = np.array([1.0, 2.0, 3.0, 4.0])
    x_test = x_test.reshape(1, 4)
    print(quick_predict(
        "D:\Program\Github\ML-Platform\Backend\ml\logreg_iris.onnx", "onnx", x_test))
