using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Python4CPM
{
    public class ChangeAction : BaseAction
    {
        private const string ACTION = "changepass";

        public ChangeAction(List<IAccount> accountList, ILogger logger)
            :base(accountList, logger)
        {
        }

        protected override bool RequiresNewPassword
        {
            get { return true; }
        }

        override public CPMAction ActionName
        {
            get { return CPMAction.changepass; }
        }

        override public int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            Logger.WriteLine($"Running action: {ACTION}", LogLevel.INFO);
            return RunAndReturn(ACTION, ref platformOutput);
        }
    }
}
