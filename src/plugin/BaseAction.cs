using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using CyberArk.Extensions.Utilties.Reader;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System;

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
        private const string PARAMS_PYTHON_EXE_PATH = "PythonExePath";
        private const string PARAMS_PYTHON_SCRIPT_PATH = "PythonScriptPath";
        private const string PARAMS_PYTHON_LOGGING = "PythonLogging";
        private const string PARAMS_PYTHON_LOGGING_LEVEL = "PythonLoggingLevel";
        protected const int CLOSE_SUCCESS = 0;
        protected const int CLOSE_FAILED_UNRECOVERABLE = 8900;
        protected const int CLOSE_FAILED_RECOVERABLE = 8100;
        public const int PYTHON_CLOSE_FAILED_UNRECOVERABLE = 89;
        public const int PYTHON_CLOSE_FAILED_RECOVERABLE = 81;
        private string PythonExePath = String.Empty;
        private string PythonScriptPath = String.Empty;
        private string Address = String.Empty;
        private string Username = String.Empty;
        private string LogonUsername = String.Empty;
        private string ReconcileUsername = String.Empty;
        private string PythonLogging = String.Empty;
        private string PythonLoggingLevel = String.Empty;
        private string CurrentPassword = String.Empty;
        private string LogonCurrentPassword = String.Empty;
        private string ReconcileCurrentPassword = String.Empty;
        private string NewPassword = String.Empty;

        public BaseAction(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected abstract bool RequiresNewPassword
        {
            get;
        }

        protected void GetFields()
        {
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PARAMS_PYTHON_EXE_PATH) == true)
            {
                PythonExePath = TargetAccount.ExtraInfoProp[PARAMS_PYTHON_EXE_PATH];
            }
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PARAMS_PYTHON_SCRIPT_PATH) == true)
            {
                PythonScriptPath = TargetAccount.ExtraInfoProp[PARAMS_PYTHON_SCRIPT_PATH];
            }
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PARAMS_PYTHON_LOGGING) == true)
            {
                PythonLogging = TargetAccount.ExtraInfoProp[PARAMS_PYTHON_LOGGING];
            }
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PARAMS_PYTHON_LOGGING_LEVEL) == true)
            {
                PythonLoggingLevel = TargetAccount.ExtraInfoProp[PARAMS_PYTHON_LOGGING_LEVEL];
            }
            Logger.WriteLine($"{PARAMS_PYTHON_EXE_PATH}: {PythonExePath}", LogLevel.INFO);
            Logger.WriteLine($"{PARAMS_PYTHON_SCRIPT_PATH}: {PythonScriptPath}", LogLevel.INFO);
            Logger.WriteLine($"{PARAMS_PYTHON_LOGGING}: {PythonLogging}", LogLevel.INFO);
            Logger.WriteLine($"{PARAMS_PYTHON_LOGGING_LEVEL}: {PythonLoggingLevel}", LogLevel.INFO);
            if (!File.Exists(PythonExePath))
                throw new FileNotFoundException(
                    $"{PARAMS_PYTHON_EXE_PATH}: {PythonExePath} does not exist"
                );
            if (!File.Exists(PythonScriptPath))
                throw new FileNotFoundException(
                    $"{PARAMS_PYTHON_SCRIPT_PATH}: {PythonScriptPath} does not exist"
                );
            if (TargetAccount?.AccountProp?.ContainsKey("address") == true)
            {
                Address = TargetAccount.AccountProp["address"];
            }
            if (TargetAccount?.AccountProp?.ContainsKey("username") == true)
            {
                Username = TargetAccount.AccountProp["username"];
            }
            if (LogOnAccount?.AccountProp?.ContainsKey("username") == true)
            {
                LogonUsername = LogOnAccount.AccountProp["username"];
            }
            if (ReconcileAccount?.AccountProp?.ContainsKey("username") == true)
            {
                ReconcileUsername = ReconcileAccount.AccountProp["username"];
            }
            if (TargetAccount?.CurrentPassword != null)
            {
                CurrentPassword = Crypto.Encrypt(TargetAccount.CurrentPassword);
            }
            if (LogOnAccount?.CurrentPassword != null)
            {
                LogonCurrentPassword = Crypto.Encrypt(LogOnAccount.CurrentPassword);
            }
            if (ReconcileAccount?.CurrentPassword != null)
            {
                ReconcileCurrentPassword = Crypto.Encrypt(ReconcileAccount.CurrentPassword);
            }
            if (RequiresNewPassword)
            {
                if (TargetAccount?.NewPassword == null)
                {
                    throw new InvalidOperationException("Required TargetAccount.NewPassword is null");
                }
                NewPassword = Crypto.Encrypt(TargetAccount.NewPassword);
            }
        }

        private Dictionary<string, string> GetEnv(string action)
        {
            return new Dictionary<string, string>
            {
                { ENV_ACTION, action },
                { ENV_ADDRESS, Address },
                { ENV_USERNAME, Username },
                { ENV_LOGON_USERNAME, LogonUsername },
                { ENV_RECONCILE_USERNAME, ReconcileUsername },
                { ENV_LOGGING, PythonLogging },
                { ENV_LOGGING_LEVEL, PythonLoggingLevel },
                { ENV_PASSWORD, CurrentPassword },
                { ENV_LOGON_PASSWORD, LogonCurrentPassword },
                { ENV_RECONCILE_PASSWORD, ReconcileCurrentPassword },
                { ENV_NEW_PASSWORD, NewPassword }
            };
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
                GetFields();
            }
            catch (Exception ex)
            {
                return HandleException(ex, true, ref platformOutput);
            }
            try
            {
                RunScript(action);
                Logger.WriteLine("Closing with success", LogLevel.INFO);
                return CLOSE_SUCCESS;
            }
            catch (PythonExecutionException ex)
            {
                if (ex.ExitCode == PYTHON_CLOSE_FAILED_RECOVERABLE)
                {
                    return HandleException(ex, false, ref platformOutput);
                }
                return HandleException(ex, true, ref platformOutput);
            }
            catch (Exception ex)
            {
                return HandleException(ex, true, ref platformOutput);
            }
        }

        private int HandleException(Exception ex, bool unrecoverable, ref PlatformOutput platformOutput)
        {
            string message = $"{ex.GetType()}: {ex.Message}";
            platformOutput.Message = message;
            Logger.WriteLine(message, LogLevel.ERROR);
            if (!unrecoverable)
            {
                Logger.WriteLine("Closing with failed recoverable", LogLevel.ERROR);
                return CLOSE_FAILED_RECOVERABLE;
            }
            else
            {
                Logger.WriteLine("Closing with failed unrecoverable", LogLevel.ERROR);
                return CLOSE_FAILED_UNRECOVERABLE;
            }
        }
    }
}
