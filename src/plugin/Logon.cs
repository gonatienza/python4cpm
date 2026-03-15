using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Logon : BaseAction
    {
        private const string Action = "logon";

        public Logon(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected override bool RequiresNewPassword => false;

        public override CPMAction ActionName => CPMAction.logon;

        public override int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            int rc = RunAction(Action, ref platformOutput);
            Logger.MethodEnd();
            return rc;
        }
    }
}
