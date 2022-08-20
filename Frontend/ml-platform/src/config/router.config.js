// eslint-disable-next-line
import { UserLayout, BasicLayout, BlankLayout } from '@/layouts'
// import { bxAnaalyse } from '@/core/icons'

const RouteView = {
  name: 'RouteView',
  render: h => h('router-view')
}

export const asyncRouterMap = [
  {
    path: '/',
    name: 'index',
    component: BasicLayout,
    meta: { title: 'menu.home' },
    redirect: '/model',
    children: [
      {
        path: '/model',
        redirect: '/model/model-list',
        component: RouteView,
        meta: { title: 'Model', icon: 'table', permission: ['table'] },
        children: [
          {
            path: '/model/model-add',
            name: 'ModelAdd',
            component: () => import('@/views/model/modelAdd'),
            meta: { title: 'Add model', keepAlive: true, permission: ['form'] }
          },
          {
            path: '/model/model-list',
            name: 'ModelList',
            component: () => import('@/views/model/modelList'),
            meta: { title: 'Model list', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/model/model-test',
            name: 'ModelTest',
            component: () => import('@/views/model/modelTest'),
            meta: { title: 'Test model', keepAlive: true, permission: ['form'] },
            hidden: true
          }
        ]
      },
      {
        path: '/deploy',
        name: 'deploy',
        component: RouteView,
        redirect: '/deploy/deploy-list',
        meta: { title: 'Deploy', icon: 'table', permission: ['table'] },
        children: [
          {
            path: '/deploy/deploy-add',
            name: 'DeployModel',
            component: () => import('@/views/deploy/serviceAdd'),
            meta: { title: 'Deploy model', keepAlive: true, permission: ['form'] },
            hidden: true
          },
          {
            path: '/deploy/deploy-list',
            name: 'DeployList',
            component: () => import('@/views/deploy/serviceList'),
            meta: { title: 'Service List', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/deploy/deploy-test',
            name: 'DeployTest',
            component: () => import('@/views/deploy/serviceTest'),
            meta: { title: 'Test service', keepAlive: true, permission: ['table'] },
            hidden: true
          }
        ]
      },
      {
        path: '/test',
        name: 'Test',
        component: RouteView,
        redirect: '/test/test-list',
        meta: { title: 'Test', icon: 'table', permission: ['table'] },
        children: [
          {
            path: '/test/test-list',
            name: 'TestList',
            component: () => import('@/views/test/testList'),
            meta: { title: 'Test List', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/test/test-detail',
            name: 'TestDatail',
            component: () => import('@/views/test/testDetail'),
            meta: { title: 'Test Detail', keepAlive: true, permission: ['table'] },
            hidden: true
          }
        ]
      }
    ]
  },
  {
    path: '*',
    redirect: '/404',
    hidden: true
  }
]

/**
 * 基础路由
 * @type { *[] }
 */
export const constantRouterMap = [
  {
    path: '/404',
    component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/404')
  }
]
