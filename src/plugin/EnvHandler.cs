using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class EnvHandler
    {
        private const string Prefix = "python4cpm_";
        private const string ArgsObjPrefix = "args_";
        private const string TargetAccountObjPrefix = "target_";
        private const string LogonAccountObjPrefix = "logon_";
        private const string ReconcileAccountObjPrefix = "reconcile_";
        private const string ActionKey = "action";
        private const string LoggingLevelKey = "logging_level";
        private const string UsernameKey = "username";
        private const string AddressKey = "address";
        private const string PortKey = "port";
        private const string PasswordKey = "password";
        private const string NewPasswordKey = "new_password";

        private static string GetEnvKey(string objPrefix, string key)
        {
            string env_key = $"{Prefix}{objPrefix}{key}";
            return env_key.ToUpper();
        }

        private static string GetArgsKey(string key)
        {
            return GetEnvKey(ArgsObjPrefix, key);
        }

        private static string GetTargetAccountKey(string key)
        {
            return GetEnvKey(TargetAccountObjPrefix, key);
        }

        private static string GetLogonAccountKey(string key)
        {
            return GetEnvKey(LogonAccountObjPrefix, key);
        }

        private static string GetReconcileAccountKey(string key)
        {
            return GetEnvKey(ReconcileAccountObjPrefix, key);
        }

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
            args[GetArgsKey(ActionKey)] = action;
            if (targetUsername != null)
                args[GetTargetAccountKey(UsernameKey)] = targetUsername;
            if (targetAddress != null)
                args[GetTargetAccountKey(AddressKey)] = targetAddress;
            if (targetPort != null)
                args[GetTargetAccountKey(PortKey)] = targetPort;
            if (logonUsername != null)
                args[GetLogonAccountKey(UsernameKey)] = logonUsername;
            if (reconcileUsername != null)
                args[GetReconcileAccountKey(UsernameKey)] = reconcileUsername;
            if (pythonLoggingLevel != null)
                args[GetArgsKey(LoggingLevelKey)] = pythonLoggingLevel;
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
                secrets[GetTargetAccountKey(PasswordKey)] = targetCurrentPassword;
            if (logonCurrentPassword != null)
                secrets[GetLogonAccountKey(PasswordKey)] = logonCurrentPassword;
            if (reconcileCurrentPassword != null)
                secrets[GetReconcileAccountKey(PasswordKey)] = reconcileCurrentPassword;
            if (targetNewPassword != null)
                secrets[GetTargetAccountKey(NewPasswordKey)] = targetNewPassword;
            return secrets;
        }
    }
}
