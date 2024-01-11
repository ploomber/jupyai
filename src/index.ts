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
  id: 'jupyai:plugin',
  description:
    'JupyAI is an experimental package to add AI capabilities to JupyterLab.',
  autoStart: true,
  optional: [ISettingRegistry],
  requires: [INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    tracker: INotebookTracker,
    settingRegistry: ISettingRegistry | null
  ) => {
    console.log('JupyterLab extension jupyai is activated!');

    // getting an error when calling .load
    // if (settingRegistry) {
    //   settingRegistry
    //     .load(plugin.id)
    //     .then(settings => {
    //       console.log('jupyai settings loaded:', settings.composite);
    //     })
    //     .catch(reason => {
    //       console.error('Failed to load settings for jupyai.', reason);
    //     });
    // }

    const { commands } = app;

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

          Notification.info('Running AI Autocomplete...', { autoClose: 1000 });

          requestAPI<any>('autocomplete', {
            body: JSON.stringify({
              cell: current.model.sharedModel.toJSON(),
              sources: sources
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
