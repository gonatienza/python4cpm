using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Reconcile : BaseAction
    {
        private const string Action = "reconcilepass";

        public Reconcile(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }
        protected override bool RequiresNewPassword => true;

        public override CPMAction ActionName => CPMAction.reconcilepass;

        public override int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            int rc = RunAction(Action, ref platformOutput);
            Logger.MethodEnd();
            return rc;
        }
    }
}
