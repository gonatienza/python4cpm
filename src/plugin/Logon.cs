using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class Logon : BaseAction
    {
        private const string ACTION = "logon";

        public Logon(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected override bool RequiresNewPassword
        {
            get { return false; }
        }

        override public CPMAction ActionName
        {
            get { return CPMAction.logon; }
        }

        override public int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            Logger.WriteLine($"Running action: {ACTION}", LogLevel.INFO);
            return RunAction(ACTION, ref platformOutput);
        }
    }
}
