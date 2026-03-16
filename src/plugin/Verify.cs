using System.Collections.Generic;
using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Verify : BaseAction
    {
        private const string Action = "verifypass";

        public Verify(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        public override CPMAction ActionName => CPMAction.verifypass;

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
