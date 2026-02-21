using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using CyberArk.Extensions.Utilties.Reader;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace CyberArk.Extensions.Python4CPM
{
    abstract public class BaseAction : AbsAction
    {
        private const string ENV_ACTION = "PYTHON4CPM_ACTION";
        private const string ENV_ADDRESS = "PYTHON4CPM_ADDRESS";
        private const string ENV_USERNAME = "PYTHON4CPM_USERNAME";
        private const string ENV_LOGON_USERNAME = "PYTHON4CPM_LOGON_USERNAME";
        private const string ENV_RECONCILE_USERNAME = "PYTHON4CPM_RECONCILE_USERNAME";
        private const string ENV_LOGGING = "PYTHON4CPM_LOGGING";
        private const string ENV_LOGGING_LEVEL = "PYTHON4CPM_LOGGING_LEVEL";
        private const string ENV_PASSWORD = "PYTHON4CPM_PASSWORD";
        private const string ENV_LOGON_PASSWORD = "PYTHON4CPM_LOGON_PASSWORD";
        private const string ENV_RECONCILE_PASSWORD = "PYTHON4CPM_RECONCILE_PASSWORD";
        private const string ENV_NEW_PASSWORD = "PYTHON4CPM_NEW_PASSWORD";
        private const string PYTHON_EXE_PATH = "PythonExePath";
        private const string PYTHON_SCRIPT_PATH = "PythonScriptPath";
        private const string PYTHON_LOGGING = "PythonLogging";
        private const string PYTHON_LOGGING_LEVEL = "PythonLoggingLevel";
        protected const int CLOSE_SUCCESS = 0;
        protected const int CLOSE_FAILED_UNRECOVERABLE = 8900;
        protected const int CLOSE_FAILED_RECOVERABLE = 8100;
        public const int PYTHON_CLOSE_FAILED_UNRECOVERABLE = 89;
        public const int PYTHON_CLOSE_FAILED_RECOVERABLE = 81;
        private string PythonExePath;
        private string PythonScriptPath;
        private string PythonLogging;
        private string PythonLoggingLevel;

        public BaseAction(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected abstract bool RequiresNewPassword
        {
            get;
        }

        protected void GetParams()
        {
            PythonExePath = TargetAccount.ExtraInfoProp[PYTHON_EXE_PATH];
            PythonScriptPath = TargetAccount.ExtraInfoProp[PYTHON_SCRIPT_PATH];
            PythonLogging = TargetAccount.ExtraInfoProp[PYTHON_LOGGING];
            PythonLoggingLevel = TargetAccount.ExtraInfoProp[PYTHON_LOGGING_LEVEL];
            Logger.WriteLine($"{PYTHON_EXE_PATH}: {PythonExePath}", LogLevel.INFO);
            Logger.WriteLine($"{PYTHON_SCRIPT_PATH}: {PythonScriptPath}", LogLevel.INFO);
            Logger.WriteLine($"{PYTHON_LOGGING}: {PythonLogging}", LogLevel.INFO);
            Logger.WriteLine($"{PYTHON_LOGGING_LEVEL}: {PythonLoggingLevel}", LogLevel.INFO);
            if (!File.Exists(PythonExePath))
                throw new FileNotFoundException(
                    $"{PYTHON_EXE_PATH}: {PythonExePath} does not exist"
                );
            if (!File.Exists(PythonScriptPath))
                throw new FileNotFoundException(
                    $"{PYTHON_SCRIPT_PATH}: {PythonScriptPath} does not exist"
                );
        }

        private Dictionary<string, string> GetEnv(string action)
        {
            string address = string.Empty;
            string username = string.Empty;
            string logonUsername = string.Empty;
            string reconcileUsername = string.Empty;
            string currentPassword = string.Empty;
            string logonCurrentPassword = string.Empty;
            string reconcileCurrentPassword = string.Empty;
            string newPassword = string.Empty;
            if (TargetAccount.AccountProp.ContainsKey("address"))
            {
                address = TargetAccount.AccountProp["address"];
            }
            if (TargetAccount.AccountProp.ContainsKey("username"))
            {
                username = TargetAccount.AccountProp["username"];
            }
            if (LogOnAccount != null && LogOnAccount.AccountProp.ContainsKey("username"))
            {
                logonUsername = LogOnAccount.AccountProp["username"];
            }
            if (ReconcileAccount != null && ReconcileAccount.AccountProp.ContainsKey("username"))
            {
                reconcileUsername = ReconcileAccount.AccountProp["username"];
            }
            if (username != string.Empty)
            {
                currentPassword = Crypto.Encrypt(TargetAccount.CurrentPassword);
            }
            if (logonUsername != string.Empty)
            {
                logonCurrentPassword = Crypto.Encrypt(LogOnAccount.CurrentPassword);
            }
            if (reconcileUsername != string.Empty)
            {
                reconcileCurrentPassword = Crypto.Encrypt(ReconcileAccount.CurrentPassword);
            }
            if (RequiresNewPassword)
            {
                newPassword = Crypto.Encrypt(TargetAccount.NewPassword);
            }
            var envVars = new Dictionary<string, string>
            {
                { ENV_ACTION, action },
                { ENV_ADDRESS, address },
                { ENV_USERNAME, username },
                { ENV_LOGON_USERNAME, logonUsername },
                { ENV_RECONCILE_USERNAME, reconcileUsername },
                { ENV_LOGGING, PythonLogging },
                { ENV_LOGGING_LEVEL, PythonLoggingLevel },
                { ENV_PASSWORD, currentPassword },
                { ENV_LOGON_PASSWORD, logonCurrentPassword },
                { ENV_RECONCILE_PASSWORD, reconcileCurrentPassword },
                { ENV_NEW_PASSWORD, newPassword }
            };

            return envVars;
        }

        private void RunScript(string action)
        {
            var envVars = GetEnv(action);
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = PythonExePath,
                    Arguments = $"\"{PythonScriptPath}\"",
                    UseShellExecute = false,
                    RedirectStandardInput = false,
                    RedirectStandardOutput = false,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };

            foreach (var env in envVars)
            {
                Logger.WriteLine($"Setting environment variable: {env.Key}", LogLevel.INFO);
                process.StartInfo.EnvironmentVariables[env.Key] = env.Value;
            }
            Logger.WriteLine($"Executing: {PythonExePath} {PythonScriptPath}", LogLevel.INFO);
            process.Start();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            string message = $"Python closed with exit code: {process.ExitCode}";
            if (process.ExitCode != 0)
            {
                Logger.WriteLine(message, LogLevel.ERROR);
                if (!string.IsNullOrWhiteSpace(stderr))
                {
                    Logger.WriteLine($"StdErr Output: \n{stderr}", LogLevel.ERROR);
                }
                throw new PythonExecutionException(process.ExitCode);
            }
            Logger.WriteLine(message, LogLevel.INFO);
        }

        protected int RunAction(string action, ref PlatformOutput platformOutput)
        {
            try
            {
                GetParams();
            }
            catch (FileNotFoundException ex)
            {
                platformOutput.Message = ex.Message;
                return CLOSE_FAILED_UNRECOVERABLE;
            }
            try
            {
                RunScript(action);
                return CLOSE_SUCCESS;
            }
            catch (PythonExecutionException ex)
            {
                platformOutput.Message = ex.Message;
                if (ex.ExitCode == PYTHON_CLOSE_FAILED_UNRECOVERABLE)
                {
                    return CLOSE_FAILED_UNRECOVERABLE;
                }
                return CLOSE_FAILED_RECOVERABLE;
            }
        }
    }
}
