using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Reconcile : BaseAction
    {
        private const string ACTION = "reconcilepass";

        public Reconcile(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected override bool RequiresNewPassword
        {
            get { return true; }
        }

        override public CPMAction ActionName
        {
            get { return CPMAction.reconcilepass; }
        }

        override public int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            Logger.WriteLine($"Running action: {ACTION}", LogLevel.INFO);
            return RunAction(ACTION, ref platformOutput);
        }
    }
}
