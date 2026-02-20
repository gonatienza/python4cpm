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
        protected const int PYTHON_CLOSE_FAILED_UNRECOVERABLE = 89;
        protected const int PYTHON_CLOSE_FAILED_RECOVERABLE = 81;
        private string PythonExePath;
        private string PythonScriptPath;
        private string PythonLogging;
        private string PythonLoggingLevel;

        public BaseAction(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
            PythonExePath = TargetAccount.ExtraInfoProp[PYTHON_EXE_PATH];
            PythonScriptPath = TargetAccount.ExtraInfoProp[PYTHON_SCRIPT_PATH];
            PythonLogging = TargetAccount.ExtraInfoProp[PYTHON_LOGGING];
            PythonLoggingLevel = TargetAccount.ExtraInfoProp[PYTHON_LOGGING_LEVEL];
            Logger.WriteLine($"{PYTHON_EXE_PATH}: {PythonExePath}", LogLevel.INFO);
            Logger.WriteLine($"{PYTHON_SCRIPT_PATH}: {PythonScriptPath}", LogLevel.INFO);
            Logger.WriteLine($"{PYTHON_LOGGING}: {PythonLogging}", LogLevel.INFO);
            Logger.WriteLine($"{PYTHON_LOGGING_LEVEL}: {PythonLoggingLevel}", LogLevel.INFO);
        }

        private Dictionary<string,string> GetEnv(string action)
        {
            string currentPasswordEncBase64 = Crypto.Encrypt(TargetAccount.CurrentPassword);
            string logonCurrentPasswordEncBase64 = Crypto.Encrypt(LogOnAccount.CurrentPassword);
            string reconcileCurrentPasswordEncBase64 = Crypto.Encrypt(ReconcileAccount.CurrentPassword);
            string newPasswordEncBase64 = Crypto.Encrypt(TargetAccount.NewPassword);
            var envVars = new Dictionary<string, string>
            {
                { ENV_ACTION, action },
                { ENV_ADDRESS, TargetAccount.AccountProp["address"] },
                { ENV_USERNAME, TargetAccount.AccountProp["username"] },
                { ENV_LOGON_USERNAME, LogOnAccount.AccountProp["username"] },
                { ENV_RECONCILE_USERNAME, ReconcileAccount.AccountProp["username"] },
                { ENV_LOGGING, PythonLogging },
                { ENV_LOGGING_LEVEL, PythonLoggingLevel },
                { ENV_PASSWORD, currentPasswordEncBase64 },
                { ENV_LOGON_PASSWORD, logonCurrentPasswordEncBase64 },
                { ENV_RECONCILE_PASSWORD, reconcileCurrentPasswordEncBase64 },
                { ENV_NEW_PASSWORD, newPasswordEncBase64 }
            };
            return envVars;
        }

        protected void PreRunScriptValidation()
        {
            if (!File.Exists(PythonExePath))
                throw new FileNotFoundException(
                    $"{PYTHON_EXE_PATH}: {PythonExePath} does not exist"
                );
            if (!File.Exists(PythonScriptPath))
                throw new FileNotFoundException(
                    $"{PYTHON_SCRIPT_PATH}: {PythonScriptPath} does not exist"
                );
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
            if (process.ExitCode != 0)
            {
                string message = $"Python failed with exit code: {process.ExitCode}";
                Logger.WriteLine(message, LogLevel.ERROR);
                if (!string.IsNullOrWhiteSpace(stderr))
                {
                    Logger.WriteLine($"StdErr Output: \n{stderr}", LogLevel.ERROR);
                }
                throw new PythonExecutionException(message, process.ExitCode);
            }
        }

        protected int RunAndReturn(string action, ref PlatformOutput platformOutput)
        {
            Logger.MethodStart();
            Logger.WriteLine($"Running action: {action}", LogLevel.INFO);

            try
            {
                PreRunScriptValidation();
            }
            catch (FileNotFoundException ex)
            {
                platformOutput.Message = $"Received exception: {ex.Message}.";
                return CLOSE_FAILED_UNRECOVERABLE;
            }
            try
            {
                RunScript(action);
                return CLOSE_SUCCESS;
            }
            catch (PythonExecutionException ex)
            {
                platformOutput.Message = $"Received exception: {ex.Message}.";
                if (ex.ExitCode == PYTHON_CLOSE_FAILED_UNRECOVERABLE)
                {
                    return CLOSE_FAILED_UNRECOVERABLE;
                }
                return CLOSE_FAILED_RECOVERABLE;
            }
        }
    }
}
