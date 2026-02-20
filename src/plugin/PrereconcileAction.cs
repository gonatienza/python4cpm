using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Python4CPM
{
    public class PrereconcileAction : BaseAction
    {
        private const string ACTION = "prereconcilepass";

        public PrereconcileAction(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected override bool RequiresNewPassword
        {
            get { return false; }
        }

        override public CPMAction ActionName
        {
            get { return CPMAction.prereconcilepass; }
        }

        override public int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            Logger.WriteLine($"Running action: {ACTION}", LogLevel.INFO);
            return RunAndReturn(ACTION, ref platformOutput);
        }
    }
}
