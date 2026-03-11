using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Prereconcile : BaseAction
    {
        private const string Action = "prereconcilepass";

        public Prereconcile(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        override public CPMAction ActionName
        {
            get { return CPMAction.prereconcilepass; }
        }

        override public int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            Logger.WriteLine($"Running action: {Action}", LogLevel.INFO);
            return RunAction(Action, ref platformOutput);
        }
    }
}
