using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Change : BaseAction
    {
        private const string Action = "changepass";

        public Change(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected override bool RequiresNewPassword => true;

        public override CPMAction ActionName => CPMAction.changepass;

        public override int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            int rc = RunAction(Action, ref platformOutput);
            Logger.MethodEnd();
            return rc;
        }
    }
}
