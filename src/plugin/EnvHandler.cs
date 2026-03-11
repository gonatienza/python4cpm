using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class EnvHandler
    {
        private const string Action = "PYTHON4CPM_ARGS_ACTION";
        private const string LoggingLevel = "PYTHON4CPM_ARGS_LOGGING_LEVEL";
        private const string TargetUsername = "PYTHON4CPM_TARGET_USERNAME";
        private const string TargetAddress = "PYTHON4CPM_TARGET_ADDRESS";
        private const string TargetPort = "PYTHON4CPM_TARGET_PORT";
        private const string LogonUsername = "PYTHON4CPM_LOGON_USERNAME";
        private const string ReconcileUsername = "PYTHON4CPM_RECONCILE_USERNAME";
        private const string TargetPassword = "PYTHON4CPM_TARGET_PASSWORD";
        private const string LogonPassword = "PYTHON4CPM_LOGON_PASSWORD";
        private const string ReconcilePassword = "PYTHON4CPM_RECONCILE_PASSWORD";
        private const string TargetNewPassword = "PYTHON4CPM_TARGET_NEW_PASSWORD";

        public static Dictionary<string, string> GetArgs(
            string action,
            string targetUsername,
            string targetAddress,
            string targetPort,
            string logonUsername,
            string reconcileUsername,
            string pythonLoggingLevel)
        {
            var args = new Dictionary<string, string>();
            args[Action] = action;
            if (targetUsername != null)
                args[TargetUsername] = targetUsername;
            if (targetAddress != null)
                args[TargetAddress] = targetAddress;
            if (targetPort != null)
                args[TargetPort] = targetPort;
            if (logonUsername != null)
                args[LogonUsername] = logonUsername;
            if (reconcileUsername != null)
                args[ReconcileUsername] = reconcileUsername;
            if (pythonLoggingLevel != null)
                args[LoggingLevel] = pythonLoggingLevel;
            return args;
        }

        public static Dictionary<string, EncryptedString> GetSecrets(
            EncryptedString targetCurrentPassword,
            EncryptedString logonCurrentPassword,
            EncryptedString reconcileCurrentPassword,
            EncryptedString targetNewPassword)
        {
            var secrets = new Dictionary<string, EncryptedString>();
            if (targetCurrentPassword != null)
                secrets[TargetPassword] = targetCurrentPassword;
            if (logonCurrentPassword != null)
                secrets[LogonPassword] = logonCurrentPassword;
            if (reconcileCurrentPassword != null)
                secrets[ReconcilePassword] = reconcileCurrentPassword;
            if (targetNewPassword != null)
                secrets[TargetNewPassword] = targetNewPassword;
            return secrets;
        }
    }
}
