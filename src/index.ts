import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { requestAPI } from './handler';

/**
 * Initialization data for the jupyai extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyai:plugin',
  description: 'JupyAI is an experimental package to add AI capabilities to JupyterLab.',
  autoStart: true,
  optional: [ISettingRegistry],
  activate: (app: JupyterFrontEnd, settingRegistry: ISettingRegistry | null) => {
    console.log('JupyterLab extension jupyai is activated!');

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('jupyai settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for jupyai.', reason);
        });
    }

    requestAPI<any>('get-example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The jupyai server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
