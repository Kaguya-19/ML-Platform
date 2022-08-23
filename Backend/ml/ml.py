from __future__ import absolute_import, print_function
import sys
import json
import os
from traceback import format_exc
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score,explained_variance_score
import onnx
import onnxruntime as rt
from pyspark.ml import PipelineModel
import tensorflow as tf
from pypmml import Model

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

                y_pred = wrapped_model.model.predict(x_test)
                accuracy = accuracy_score(y_test, y_pred)
                return {
                    'accuracy': accuracy
                }
            elif function_name == FUNCTION_NAME_REGRESSION:
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
            import traceback
            traceback.print_exc()

    def model_type(self):
        return 'ONNX'

    def model_version(self):
        return None

    def mining_function(self, y_test):
        algorithm = self.algorithm()
        if algorithm is not None:
            if algorithm in ('LinearClassifier', 'SVMClassifier', 'TreeEnsembleClassifier','NeuralNetwork'):
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
            if x_test.ndim == 1:
                x_test = x_test.reshape(1,len(x_test))
            sess = self._get_inference_session()
            y_pred = None
            if len(sess.get_inputs()) == 1:
                input_name = sess.get_inputs()[0].name
                output = sess.run(None, {
                                  input_name: x_test.astype(np.float32)})
                sess = self._get_inference_session()
                output_fields = sess.get_outputs()
                for i in range(len(output_fields)):
                    result[output_fields[i].name] = output[i][0]
                return {
                    "result": [result],
                }
            else:
                return {}

        except Exception as e:
            import traceback
            return {"stderr": traceback.format_exc()}

    def batch_predict(self, x_test, input_function_name):
        if x_test is None:
            return {}

        try:
            result = []
            function_name = input_function_name if input_function_name else self.mining_function(
                None)
            # convert to numpy array if not
            x_test = self._to_ndarray(x_test).astype(np.float32)
            sess = self._get_inference_session()
            inputs = sess.get_inputs()
            if len(sess.get_inputs()) == 1:
                input_name = sess.get_inputs()[0].name
                sess = self._get_inference_session()
                output_fields = sess.get_outputs()
                if inputs[0].shape[0] == "batch_size":
                    output = sess.run(None, {input_name: x_test})
                    for i in range(x_test.shape[0]):
                        tmp_sample = {}
                        for j in range(len(output_fields)):
                            if isinstance(output[j][i],np.ndarray):
                                tmp_sample[output_fields[j].name] = output[j][i].tolist()
                            else:
                                tmp_sample[output_fields[j].name] = output[j][i]
                        result.append(tmp_sample)
                else:
                    output = [sess.run(None, {input_name: x_test[i][np.newaxis,:]}) for i in range(x_test.shape[0])]
                    for i in range(x_test.shape[0]):
                        tmp_sample = {}
                        for j in range(len(output_fields)):
                            if isinstance(output[i][j],np.ndarray):
                                tmp_sample[output_fields[j].name] = output[i][j].tolist()
                            else:
                                tmp_sample[output_fields[j].name] = output[i][j]
                        result.append(tmp_sample)
                return {
                    "result": result,
                }
            else:
                return {}

        except Exception as e:
            import traceback
            return {"stderr": traceback.format_exc()}

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
            import traceback
            return {"stderr": traceback.format_exc()}

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

            self.sess = rt.InferenceSession(
                self.onnx_model.SerializeToString())
        return self.sess


class PMMLModel(BaseModel):
    def __init__(self, model):
        BaseModel.__init__(self, model)
        self.pmml_model = None

    def __del__(self):
        if self.pmml_model:
            try:
                from pypmml import Model
                Model.close()
            except:
                pass

    def is_support(self):
        try:
            from pypmml import Model

            model_content = self.model
            if hasattr(self.model, 'read') and callable(self.model.read):
                model_content = self.model.read()

            if isinstance(model_content, (bytes, bytearray)):
                model_content = model_content.decode('utf-8')

            if isinstance(model_content, str):
                # Check if a file path
                if os.path.exists(model_content):
                    self.pmml_model = Model.fromFile(model_content)
                else:
                    self.pmml_model = Model.fromString(model_content)
                return True
            else:
                Model.close()
                return False
        except Exception as e:
            return False

    def model_type(self):
        return 'PMML'

    def model_version(self):
        return None

    def mining_function(self, y_test):
        return self.pmml_model.functionName

    def serialization(self):
        return 'pmml'

    def runtime(self):
        return 'PyPMML'

    def algorithm(self):
        return self.pmml_model.modelElement

    def quick_prediction(self, x_test, input_function_name):
        prediction_col = self.get_prediction_col()
        if prediction_col is None:
            return {}

        if x_test is not None:
            try:
                result = {}
                if x_test.ndim == 1:
                    x_test = x_test.reshape(1,len(x_test))
                y_pred = self.pmml_model.predict(x_test)
                y_pred = pd.DataFrame(y_pred)
                output_fields = self.pmml_model.outputFields
                for i in range(len(output_fields)):
                    result[output_fields[i].name] = y_pred.iat[0, i]
                return {
                    "result": result,
                }

            except Exception as e:
                import traceback
                return {"stderr": traceback.format_exc()}
        else:
            return {}

    def batch_predict(self, x_test, input_function_name):
        prediction_col = self.get_prediction_col()
        if prediction_col is None:
            return {}

        if x_test is not None:
            try:
                result = []
                output_fields = self.pmml_model.outputFields
                for i in range(x_test.shape[0]):
                    tmp = {}
                    y_pred = self.pmml_model.predict(x_test)
                    y_pred = pd.DataFrame(y_pred)
                    for i in range(len(output_fields)):
                        tmp[output_fields[i].name] = y_pred.iat[0, i]
                    result.append(tmp)
                return {
                    "result": result,
                }

            except Exception as e:
                import traceback
                return {"stderr": traceback.format_exc()}
        else:
            return {}

    def evaluate_metrics(self, x_test, y_test, data_test, input_function_name):
        prediction_col = self.get_prediction_col()
        if prediction_col is None:
            return {}

        # Convert spark df to Pandas
        if data_test is not None:
            try:
                label_col = self.pmml_model.targetName
                if not label_col:
                    return {}

                pandas_data_test = data_test.toPandas()
                y_test = pandas_data_test[label_col]
                x_test = pandas_data_test
            except:
                return {}

        if x_test is not None and y_test is not None:
            try:
                function_name = input_function_name if input_function_name else self.mining_function(
                    y_test)
                if function_name == FUNCTION_NAME_CLASSIFICATION:
                    from sklearn.metrics import accuracy_score
                    y_pred = self.pmml_model.predict(x_test)
                    accuracy = accuracy_score(y_test, y_pred[prediction_col])
                    return {
                        'accuracy': accuracy
                    }
                elif function_name == FUNCTION_NAME_REGRESSION:
                    from sklearn.metrics import explained_variance_score
                    y_pred = self.pmml_model.predict(x_test)
                    explained_variance = explained_variance_score(
                        y_test, y_pred[prediction_col])
                    return {
                        'explainedVariance': explained_variance
                    }
                else:
                    return {}
            except:
                return {}
        return {}

    def get_prediction_col(self):
        output_fields = self.pmml_model.outputFields
        for x in output_fields:
            if x.feature == 'predictedValue':
                return x.name
        return None

    def predictors(self, x_test, data_test):
        result = []

        row = None
        x_test = self._to_dataframe(x_test, data_test)
        if isinstance(x_test, pd.DataFrame):
            row = json.loads(x_test.iloc[0].to_json())

        for x in self.pmml_model.inputFields:
            result.append(({
                'name': x.name,
                'sample': row.get(x.name) if row is not None else None,
                'type': x.dataType,
                "opType": x.opType
            }))
        return result

    def targets(self, y_test, data_test):
        result = []

        row = None
        y_test = self._to_dataframe(y_test, data_test)
        if isinstance(y_test, pd.DataFrame):
            row = json.loads(y_test.iloc[0].to_json())

        for x in self.pmml_model.targetFields:
            result.append(({
                'name': x.name,
                'sample': row.get(x.name) if row is not None else None,
                'type': x.dataType
            }))
        return result

    def outputs(self, y_test, data_test, **kwargs):
        result = []
        for x in self.pmml_model.outputFields:
            result.append(({
                'name': x.name,
                'type': x.dataType
            }))
        return result


class KerasModel(BaseModel):
    def __init__(self, model):
        BaseModel.__init__(self, model)
        self.tf_keras = False

    def is_support(self):
        try:
            from keras.models import Model, load_model
            if isinstance(self.model, Model):
                return True
            if self._is_support_tf_keras():
                return True
            if isinstance(self.model, str):
                self.model = load_model(self.model)
                return True
            return False
        except:
            return self._is_support_tf_keras()

    def _is_support_tf_keras(self):
        try:
            import tensorflow as tf
            self.tf_keras = isinstance(self.model, tf.keras.Model)
            return self.tf_keras
        except:
            return False

    def model_type(self):
        return 'tf.Keras' if self.tf_keras else 'Keras'

    def model_version(self):
        if self.tf_keras:
            import tensorflow as tf
            return BaseModel.extract_major_minor_version(tf.keras.__version__)
        else:
            import keras
            return BaseModel.extract_major_minor_version(keras.__version__)

    def mining_function(self, y_test):
        return self._infer_mining_function(y_test)

    def serialization(self):
        return 'hdf5'

    def predictors(self, x_test, data_test):
        result = []

        row = None
        columns = None
        if x_test is not None:
            x_test = self._series_to_dataframe(x_test)
            shape = x_test.shape
            if isinstance(x_test, pd.DataFrame):
                row = x_test.iloc[0]
                columns = list(x_test.columns)
            else:
                row = x_test[0]

        for idx, x in enumerate(self.model.inputs):
            name = x.name
            if hasattr(self.model, 'input_names'):
                name = self.model.input_names[idx]
            tensor_shape = self._normalize_tensor_shape(x.shape)
            result.append({
                'name': name,
                'sample': [row.tolist()] if row is not None and self._compatible_shape(tensor_shape, shape) else None,
                'type': np.dtype(x.dtype.as_numpy_dtype).name,
                'shape': tensor_shape
            })

            if columns is not None and result[-1]['sample'] is not None:
                result[-1]['columns'] = columns

        return result

    def targets(self, y_test, data_test):
        if y_test is None:
            return []

        result = []
        y_test = self._series_to_dataframe(y_test)
        if isinstance(y_test, pd.DataFrame):
            row = json.loads(y_test.iloc[0].to_json())
            cols = row.keys()
            for x in cols:
                result.append(({
                    'name': x,
                    'sample': row[x],
                    'type': type(row[x]).__name__
                }))
        else:
            row = y_test[0]
            result.append({
                'name': 'tensor_target',
                'sample': row.tolist(),
                'type': y_test.dtype.name,
                'shape': self._normalize_np_shape(y_test.shape)
            })

        return result

    def outputs(self, y_test, data_test, **kwargs):
        result = []

        for idx, x in enumerate(self.model.outputs):
            name = x.name
            if hasattr(self.model, 'output_names'):
                name = self.model.output_names[idx]
            result.append(({
                'name': name,
                'type': np.dtype(x.dtype.as_numpy_dtype).name,
                'shape': self._normalize_tensor_shape(x.shape)
            }))
        return result

    def quick_prediction(self, x_test, input_function_name):
        if x_test is None:
            return {}

        try:
            import numpy as np
            import pandas as pd
            function_name = input_function_name if input_function_name else self.mining_function(
                None)
            result = []
            # convert to numpy array if not
            x_test = BaseModel._to_ndarray(x_test)
            y_pred = pd.DataFrame(self.model.predict(x_test))
            for idx, x in enumerate(self.model.outputs):
                name = x.name
                if hasattr(self.model, 'output_names'):
                    name = self.model.output_names[idx]
                result.append({
                    'name': name,
                    'value': y_pred.iat[0, idx]
                })

            return {
                "result": result
            }

        except Exception as e:
            import traceback
            return {"stderr": traceback.format_exc()}

    def batch_predict(self, x_test, input_function_name):
        if x_test is None:
            return {}

        try:
            import numpy as np
            import pandas as pd
            function_name = input_function_name if input_function_name else self.mining_function(
                None)
            result = []
            # convert to numpy array if not
            x_test = BaseModel._to_ndarray(x_test)
            y_pred = pd.DataFrame(self.model.predict(x_test))
            for i in range(y_pred.shape[0]):
                tmp = {}
                for idx, x in enumerate(self.model.outputs):
                    name = x.name
                    if hasattr(self.model, 'output_names'):
                        name = self.model.output_names[idx]
                    tmp[name] = y_pred.iat[i, idx]
                result.append(tmp)

            return {
                "result": result
            }

        except Exception as e:
            import traceback
            return {"stderr": traceback.format_exc()}

    def evaluate_metrics(self, x_test, y_test, data_test, input_function_name):
        if x_test is None or y_test is None:
            return {}

        try:
            import numpy as np
            import pandas as pd
            function_name = input_function_name if input_function_name else self.mining_function(
                y_test)

            # convert to numpy array if not
            x_test = BaseModel._to_ndarray(x_test)
            y_test = BaseModel._to_ndarray(y_test)

            shape = y_test.shape
            if len(shape) > 1 and shape[1] > 1:
                y_test = np.argmax(y_test, axis=1)

            if function_name == FUNCTION_NAME_CLASSIFICATION:
                from sklearn.metrics import accuracy_score
                y_pred = pd.DataFrame(self.model.predict(x_test)).apply(lambda x: np.argmax(np.array([x])),
                                                                        axis=1)
                accuracy = accuracy_score(y_test, y_pred)
                return {
                    'accuracy': accuracy
                }
            elif function_name == FUNCTION_NAME_REGRESSION:
                from sklearn.metrics import explained_variance_score
                y_pred = pd.DataFrame(self.model.predict(x_test))
                explained_variance = explained_variance_score(y_test, y_pred)
                return {
                    'explainedVariance': explained_variance
                }
            else:
                return {}
        except:
            return {}

    @staticmethod
    def _normalize_tensor_shape(tensor_shape):
        return [(d.value if hasattr(d, 'value') else d) for d in tensor_shape]


class SparkModel(BaseModel):
    def __init__(self, model):
        BaseModel.__init__(self, model)

    def is_support(self):
        try:
            from pyspark.ml import Model
            return isinstance(self.model, Model)
        except:
            return False

    def is_pipeline_model(self):
        try:
            from pyspark.ml import PipelineModel
            return isinstance(self.model, PipelineModel)
        except:
            return False

    def model_type(self):
        return 'Spark'

    def model_version(self):
        from pyspark import SparkConf, SparkContext
        sc = SparkContext.getOrCreate(conf=SparkConf())
        return BaseModel.extract_major_minor_version(sc.version)

    def mining_function(self, y_test):
        return BaseModel.mining_function(self, y_test)

    def serialization(self):
        return 'spark'

    def evaluate_metrics(self, x_test, y_test, data_test, input_function_name):
        if data_test is None:
            return {}

        try:
            prediction = self.model.transform(data_test)
            label_col = self.get_label_col()
            predict_col = self.get_prediction_col()
            function_name = input_function_name if input_function_name else self.mining_function(
                y_test)
            if function_name == FUNCTION_NAME_CLASSIFICATION:
                accuracy = prediction.rdd.filter(
                    lambda x: x[label_col] == x[predict_col]).count() * 1.0 / prediction.count()
                return {
                    'accuracy': accuracy
                }
            elif function_name == FUNCTION_NAME_REGRESSION:
                numerator = prediction.rdd.map(
                    lambda x: x[label_col] - x[predict_col]).variance()
                denominator = prediction.rdd.map(
                    lambda x: x[label_col]).variance()
                explained_variance = 1.0 - numerator / denominator
                return {
                    'explainedVariance': explained_variance
                }
            else:
                return {}
        except:
            return {}

    def predictors(self, x_test, data_test):
        if data_test is None:
            return []

        row = json.loads(data_test.limit(1).toPandas().iloc[0].to_json())
        label_col = self.get_label_col()
        cols = row.keys()
        result = []
        for x in cols:
            if x != label_col:
                result.append(({
                    'name': x,
                    'sample': row[x],
                    'type': type(row[x]).__name__
                }))
        return result

    def targets(self, y_test, data_test):
        if data_test is None:
            return []

        row = json.loads(data_test.limit(1).toPandas().iloc[0].to_json())
        label_col = self.get_label_col()
        cols = row.keys()
        result = []
        for x in cols:
            if x == label_col:
                result.append(({
                    'name': x,
                    'sample': row[x],
                    'type': type(row[x]).__name__
                }))
        return result

    def get_label_col(self):
        if isinstance(self.model, PipelineModel):
            stages = self.model.stages
            label_col = None
            i = 0
            for x in reversed(stages):
                try:
                    label_col = x._call_java('getLabelCol')
                    i += 1
                    break
                except:
                    pass

            # find the first input column
            reversed_stages = stages[:]
            reversed_stages.reverse()
            for x in reversed_stages[i:]:
                try:
                    if x._call_java('getOutputCol') == label_col:
                        label_col = x._call_java('getInputCol')
                except:
                    pass
            return 'label' if label_col is None else label_col
        else:
            label_col = None
            try:
                label_col = self.model._call_java('getLabelCol')
            except:
                label_col = 'label'
            return label_col

    def get_prediction_col(self):

        if isinstance(self.model, PipelineModel):
            stages = self.model.stages
            try:
                return stages[-1].getOutputCol()
            except:
                return 'prediction'
        else:
            try:
                return self.model.getPredictionCol()
            except:
                return 'prediction'


def get_model_info(path, type):
    if type == "onnx":
        model = ONNXModel(path)
    elif type == "pmml":
        model = PMMLModel(path)
    elif type == "keras":
        model = KerasModel(path)
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
    elif type == "pmml":
        model = PMMLModel(path)
    elif type == "keras":
        model = KerasModel(path)
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


def batch_predict(path, type, x_test):
    if type == "onnx":
        model = ONNXModel(path)
    elif type == "pmml":
        model = PMMLModel(path)
    elif type == "keras":
        model = KerasModel(path)
    else:
        return {
            "stderr": "Not implemented model type."
        }
    if model.is_support():
        return model.batch_predict(x_test, None)
    else:
        return {
            "stderr": "Not supported."
        }


if __name__ == "__main__":
    import os
    path = os.path.dirname(__file__)
    info = get_model_info(
        path + r"\my_model", "keras")
    print("keras: ", info)

    print("onnx: ", get_model_info(
        path + r"\logreg_iris.onnx", "onnx"))

    print("pmml: ", get_model_info(
        path + r"\xgb-iris.pmml", "pmml"
    ))
