import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { INotebookTracker } from '@jupyterlab/notebook';
import { LabIcon } from '@jupyterlab/ui-components';
import { Notification } from '@jupyterlab/apputils';

import { requestAPI } from './handler';
import { INotebookContent } from '@jupyterlab/nbformat';

const PLUGIN_ID = 'jupyai:plugin';

const CommandIds = {
  /**
   * Command to trigger AI autocomplete.
   */
  runCodeCell: 'jupyai:autocomplete'
};

const wandIcon = new LabIcon({
  name: 'jupyai:wand',
  svgstr: require('../style/wand-magic-solid.svg')
});

/**
 * Initialization data for the jupyai extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  description:
    'JupyAI is an experimental package to add AI capabilities to JupyterLab.',
  autoStart: true,
  requires: [INotebookTracker, ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    tracker: INotebookTracker,
    settings: ISettingRegistry
  ) => {
    console.log('JupyterLab extension jupyai is activated!');
    const { commands } = app;

    let modelName = 'gpt-3.5-turbo';

    /**
     * Load the settings for this extension
     *
     * @param setting Extension settings
     */
    function loadSetting(setting: ISettingRegistry.ISettings): void {
      // Read the settings and convert to the correct type
      modelName = setting.get('modelName').composite as string;

      console.log(
        `Settings Example extension: model name is set to '${modelName}'`
      );
    }

    // Wait for the application to be restored and
    // for the settings for this plugin to be loaded
    Promise.all([app.restored, settings.load(PLUGIN_ID)])
      .then(([, setting]) => {
        // Read the settings
        loadSetting(setting);

        // Listen for your plugin setting changes using Signal
        setting.changed.connect(loadSetting);
      })
      .catch(reason => {
        console.error(
          `Something went wrong when reading the settings.\n${reason}`
        );
      });

    /* Adds a command enabled only on code cell */
    commands.addCommand(CommandIds.runCodeCell, {
      icon: wandIcon,
      caption: 'Autocomplete with AI',
      execute: () => {
        const current = tracker.activeCell;

        if (current) {
          let notebook: INotebookContent | undefined;
          let sources: any;

          tracker.forEach(cell => {
            notebook = cell.model?.sharedModel.toJSON();
            sources = notebook?.cells.map(cell => ({
              source: cell.source,
              id: cell.id
            }));
          });

          Notification.info(`Running AI Autocomplete with ${modelName}`, {
            autoClose: 1000
          });

          requestAPI<any>('autocomplete', {
            body: JSON.stringify({
              cell: current.model.sharedModel.toJSON(),
              sources: sources,
              model_name: modelName
            }),
            method: 'POST'
          })
            .then(data => {
              current.model.sharedModel.source = data.data;
            })
            .catch(reason => {
              Notification.error(reason.message, {
                autoClose: 3000
              });
            });
        }
      },
      isVisible: () => tracker.activeCell?.model.type === 'code'
    });
  }
};

export default plugin;
