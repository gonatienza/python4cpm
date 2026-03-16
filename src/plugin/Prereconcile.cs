using System.Collections.Generic;
using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Prereconcile : BaseAction
    {
        private const string Action = "prereconcilepass";

        public Prereconcile(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        public override CPMAction ActionName => CPMAction.prereconcilepass;

        protected override bool RequiresNewPassword => false;

        public override int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            int rc = RunAction(Action, ref platformOutput);
            Logger.MethodEnd();
            return rc;
        }
    }
}
