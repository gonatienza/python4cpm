using System;
using System.Collections.Generic;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public class EnvHandler
    {
        private const string ACTION = "PYTHON4CPM_ARGS_ACTION";
        private const string LOGGING_LEVEL = "PYTHON4CPM_ARGS_LOGGING_LEVEL";
        private const string TARGET_USERNAME = "PYTHON4CPM_TARGET_USERNAME";
        private const string TARGET_ADDRESS = "PYTHON4CPM_TARGET_ADDRESS";
        private const string TARGET_PORT = "PYTHON4CPM_TARGET_PORT";
        private const string LOGON_USERNAME = "PYTHON4CPM_LOGON_USERNAME";
        private const string RECONCILE_USERNAME = "PYTHON4CPM_RECONCILE_USERNAME";
        private const string TARGET_PASSWORD = "PYTHON4CPM_TARGET_PASSWORD";
        private const string LOGON_PASSWORD = "PYTHON4CPM_LOGON_PASSWORD";
        private const string RECONCILE_PASSWORD = "PYTHON4CPM_RECONCILE_PASSWORD";
        private const string TARGET_NEW_PASSWORD = "PYTHON4CPM_TARGET_NEW_PASSWORD";

        public static Dictionary<string, string> GetArgs(
            string action,
            string targetUsername,
            string targetAddress,
            string targetPort,
            string logonUsername,
            string reconcileUsername,
            string pythonLoggingLevel)
        {
            return new Dictionary<string, string>
            {
                { ACTION, action },
                { TARGET_USERNAME, targetUsername },
                { TARGET_ADDRESS, targetAddress },
                { TARGET_PORT, targetPort },
                { LOGON_USERNAME, logonUsername },
                { RECONCILE_USERNAME, reconcileUsername },
                { LOGGING_LEVEL, pythonLoggingLevel }
            };
        }

        public static Dictionary<string, EncryptedString> GetSecrets(
            EncryptedString targetCurrentPassword,
            EncryptedString logonCurrentPassword,
            EncryptedString reconcileCurrentPassword,
            EncryptedString targetNewPassword)
        {
            return new Dictionary<string, EncryptedString>
            {
                { TARGET_PASSWORD, targetCurrentPassword },
                { LOGON_PASSWORD, logonCurrentPassword },
                { RECONCILE_PASSWORD, reconcileCurrentPassword },
                { TARGET_NEW_PASSWORD, targetNewPassword }
            };
        }
    }
}
