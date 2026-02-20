using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;

namespace CyberArk.Extensions.Python4CPM
{
    public class ReconcileAction : BaseAction
    {
        private const string ACTION = "reconcilepass";

        public ReconcileAction(List<IAccount> accountList, ILogger logger)
            :base(accountList, logger)
        {
        }
        
        override public CPMAction ActionName
        {
            get { return CPMAction.reconcilepass; }
        }

        override public int run(ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            Logger.WriteLine($"Running action: {ACTION}", LogLevel.INFO);

            return RunAndReturn(ACTION, ref platformOutput);
        }
    }
}
