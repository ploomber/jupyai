import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { INotebookTracker } from '@jupyterlab/notebook';
import { runIcon } from '@jupyterlab/ui-components';

import { requestAPI } from './handler';

const CommandIds = {
  /**
   * Command to trigger AI autocomplete.
   */
  runCodeCell: 'jupyai:autocomplete'
};


/**
 * Initialization data for the jupyai extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyai:plugin',
  description: 'JupyAI is an experimental package to add AI capabilities to JupyterLab.',
  autoStart: true,
  optional: [ISettingRegistry],
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker, settingRegistry: ISettingRegistry | null) => {
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
      icon: runIcon,
      caption: 'Autocomplete with AI',
      execute: () => {
        const current = tracker.activeCell

        if (current) {
          requestAPI<any>('autocomplete', {
            body: JSON.stringify(current.model.sharedModel.toJSON()),
            method: 'POST'
          })
            .then(data => {
              current.model.sharedModel.source = data.data;
            })
            .catch(reason => {
              // TODO: show popup error
              console.error(
                `The jupyai server extension appears to be missing.\n${reason}`
              );
            });


        }

      },
      isVisible: () => tracker.activeCell?.model.type === 'code'
    });

  }
};

export default plugin;
