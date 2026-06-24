window.config = {
  routerBasename: '/',
  extensions: [],
  modes: [],
  showStudyList: true,

  // v2-style config (kept for compatibility)
  servers: {
    dicomWeb: [
      {
        name: 'Orthanc',
        wadoUriRoot: 'http://localhost:8043/dicom-web',
        qidoRoot: 'http://localhost:8043/dicom-web',
        wadoRoot: 'http://localhost:8043/dicom-web',
        qidoSupportsIncludeField: true,
        imageRendering: 'wadors',
        thumbnailRendering: 'wadors'
      }
    ]
  },

  // v3-style config
  defaultDataSourceName: 'dicomweb',
  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'dicomweb',
      configuration: {
        friendlyName: 'Orthanc (local)',
        name: 'Orthanc',
        wadoUriRoot: 'http://localhost:8043/dicom-web',
        qidoRoot: 'http://localhost:8043/dicom-web',
        wadoRoot: 'http://localhost:8043/dicom-web',
        qidoSupportsIncludeField: true,
        imageRendering: 'wadors',
        thumbnailRendering: 'wadors',
        enableStudyLazyLoad: true,
        supportsFuzzyMatching: true,
        supportsWildcard: true
      }
    }
  ]
};
