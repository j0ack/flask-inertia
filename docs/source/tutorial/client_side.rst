=================
Client-side setup
=================

Build a Vue app using Typescript with the ``@vite`` tool.

Install dependencies
====================

.. code:: bash

   cd static/vue
   npm create vite@latest . -- --template vue-ts

Install the Inertia dependendencies:

.. code:: bash

   npm install --save @inertiajs/inertia @inertiajs/vue3

Reconfigure the app deleting all the auto generated files we won't need and
creating missing folders:

.. code:: bash

   rm -rfv src/App.vue src/components/ src/assets public/ index.html README.md index.html
   mkdir src/pages/

Vue configuration
=================

There are modification to the Vue configuration to make it usable with our
application:

By default, Vue embed a ``vite`` dev server to serve the app. It will be
disabled in the ``package.json`` file replacing it with a ``build`` development
mode. This task will allow you to configure a ``hot-reload`` development
environment generating the ``main.js`` file. This file will then be served by the Flask app.

.. code:: Diff

       "scripts": {
    -    "dev": "vite",
    +    "build:dev": "vite build --mode=development --watch",
    +    "build:prod": "vite build",
         "build": "vue-tsc -b && vite build",
         "preview": "vite preview"
       }

Vue needs to be configured to generate the JavaScript code into the ``static/dist``
as configured in the server-side application. Based on the application architecture,
there will be no need to generate a html file with Vue since our ``base.html``
will be rendered by Flask. Those configuration are stored in a ``vite.config.js``
file in the ``static/vue`` folder.

.. code-block:: javascript
   :caption: vite.config.js

   import { fileURLToPath, URL } from 'node:url'
   import { defineConfig } from 'vite'
   import vue from '@vitejs/plugin-vue'

   // https://vitejs.dev/config/
   export default defineConfig(({ command, mode, ssrBuild }) => {
     const config = {
       plugins: [vue()],
       resolve: {
         alias: {
           '@': fileURLToPath(new URL('./src', import.meta.url))
         }
       },
       base: '/dist'
     };
     const buildConfig = {
       outDir: '../dist/',
       emptyOutDir: true,
       rollupOptions: {
         input: 'src/main.ts',
         output: {
           entryFileNames: '[name].js',
           assetFileNames: 'assets/[name].[ext]'
         }
       }
     };

     return {
       ...config,
       build: buildConfig
     }
   });

Integrate Inertia
=================

Modify the ``static/vue/src/main.ts`` file as followed:


.. code-block:: typescript
   :caption: main.ts

   import { createApp, h } from 'vue'
   import type { App } from 'vue'
   import { createInertiaApp } from '@inertiajs/vue3'


   type StrOrNum = string | number

   declare global {
     interface Window {
       reverseUrl(
         urlName: string, args?: Record<string, unknown> | StrOrNum | StrOrNum[]
       ): string
     }
   }

   // create a plugin to use window.reverseUrl in our Components
   const routePlugin = {
     install: (app: App, _options: Record<string, unknown>) => {
       app.config.globalProperties.$route = window.reverseUrl
     }
   }

   createInertiaApp({
     resolve: name => {
       const pages = import.meta.glob('./pages/**/*.vue', { eager: true })
       return pages[`./pages/${name}.vue`]
     },
     setup({ el, App, props, plugin }) {
       const vueApp = createApp({ render: () => h(App, props) })
       vueApp.use(plugin)
       vueApp.use(routePlugin)
       vueApp.mount(el)
     }
   })


In order to tell ``TypeScript`` about this new property ``$route``, we are going to use
module augmentation as mentioned in
`Vue 3 documentation <https://v3.vuejs.org/guide/typescript-support.html#augmenting-types-for-globalproperties>`_.

Create a new ``route-plugin.d.ts`` which will be used by ``TypeScript`` to determine
components' global methods:

.. code-block:: typescript
   :caption: route-plugin.d.ts

   import { Inertia } from '@inertiajs/inertia'

   type StrOrNum = string | number

   declare module '@vue/runtime-core' {
     export interface ComponentCustomProperties {
       $route: (urlName: string, args?: Record<string, unknown> | StrOrNum | StrOrNum[]): string
       $inertia: typeof Inertia
     }
   }

Create your views
=================

In the :doc:`server_side` chapter we created two views: ``index`` and ``params``.
These views use respectively a ``Index.vue`` and a ``Params.vue`` file stored
in the ``static/vue/src/pages`` folder. It can be implemented as followed:

.. code-block:: vue
   :caption: Index.vue

   <script lang="ts" setup>
     import { PropType } from 'vue'

     defineProps({
      foo: {
        type: String as PropType<string>,
        required: true
      },
      fiz: {
        type: String as PropType<string>,
        required: true
      },
      num: {
        type: Number as PropType<number>,
        required: true
      },
     })
   </script>

   <template>
     <div class="content">
       <p class="field">
         <span class="label">Foo :</span>
         <span class="value">{{ foo }}</span>
       </p>
       <p class="field">
         <span class="label">Fiz :</span>
         <span class="value">{{ fiz }}</span>
       </p>
       <p class="field">
         <span class="label">Num :</span>
         <span class="value">{{ num }}</span>
       </p>
     </div>
   </template>


.. code-block:: vue
   :caption: Params.vue

   <template>
     <strong>It works</strong>
   </template>

For more options creating your views, please read the provided
`Inertia documentation <https://inertiajs.com/pages>`_.


Add links between your routes
=============================

Flask-inertia provides a ``window.reverseUrl`` client side to allow Vue to access
Flask defined routes. The line

.. code:: typescript

  app.config.globalProperties.$route = window.reverseUrl


in the ``main.ts`` file make it usable in all the application components registering a
``$route`` method as a global property.

To create Inertia requests, ``inertia-vue3`` implements a new Vue component named
``Link``. It can be used in the ``Index`` page as followed:

.. code-block:: vue
   :caption: Index.vue
   :emphasize-lines: 3,10,11,12

   <script lang="ts" setup>
     import { PropType } from 'vue'
     import { Link } from '@inertiajs/vue3'

     defineProps({ /** init props as before **/ })
   </script>

   <template>
     <div class="content">
        <Link :href="$route('params')">
          My params
        </Link>
     </div>
   </template>
