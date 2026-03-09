using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    abstract public class BaseAction : AbsAction
    {
        private const string PARAMS_PYTHON_EXE_PATH = "PythonExePath";
        private const string PARAMS_PYTHON_SCRIPT_PATH = "PythonScriptPath";
        private const string PARAMS_PYTHON_LOGGING_LEVEL = "PythonLoggingLevel";
        private const string PROPERTIES_USERNAME = "username";
        private const string PROPERTIES_ADDRESS = "address";
        private const string PROPERTIES_PORT = "port";
        protected const int CLOSE_SUCCESS = 0;
        protected const int CLOSE_FAILED_UNRECOVERABLE = 8900;
        protected const int CLOSE_FAILED_RECOVERABLE = 8100;
        private const int PYTHON_CLOSE_SUCCESS = 10;
        public const int PYTHON_CLOSE_FAILED_UNRECOVERABLE = 89;
        public const int PYTHON_CLOSE_FAILED_RECOVERABLE = 81;
        private string PythonExePath = string.Empty;
        private string PythonScriptPath = string.Empty;
        private string PythonLoggingLevel = string.Empty;
        private string TargetUsername = string.Empty;
        private string TargetAddress = string.Empty;
        private string TargetPort = string.Empty;
        private string LogonUsername = string.Empty;
        private string ReconcileUsername = string.Empty;
        private EncryptedString TargetCurrentPassword = new EncryptedString(string.Empty);
        private EncryptedString LogonCurrentPassword = new EncryptedString(string.Empty);
        private EncryptedString ReconcileCurrentPassword = new EncryptedString(string.Empty);
        private EncryptedString TargetNewPassword = new EncryptedString(string.Empty);

        public BaseAction(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected abstract bool RequiresNewPassword
        {
            get;
        }

        private string GetLoggingValue(object obj)
        {
            string logValue;
            if (obj is EncryptedString enc && enc.Secret != string.Empty)
            {
                logValue = "[ENCRYPTED]";
            }
            else if (obj is string str && str != string.Empty)
            {
                logValue = $"'{str}'";
            }
            else
            {
                logValue = "[NOT SET]";
            }
            return logValue;
        }

        private void LogField(string name, object obj)
        {
            string logValue = GetLoggingValue(obj);
            Logger.WriteLine($"{name} -> {logValue}", LogLevel.INFO);
        }

        private void LogEnvVar(string name, object obj)
        {
            string logValue = GetLoggingValue(obj);
            Logger.WriteLine($"'{name}' -> {logValue}", LogLevel.INFO);
        }

        private void GetParams()
        {
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PARAMS_PYTHON_EXE_PATH) == true)
                PythonExePath = TargetAccount.ExtraInfoProp[PARAMS_PYTHON_EXE_PATH];
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PARAMS_PYTHON_SCRIPT_PATH) == true)
                PythonScriptPath = TargetAccount.ExtraInfoProp[PARAMS_PYTHON_SCRIPT_PATH];
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PARAMS_PYTHON_LOGGING_LEVEL) == true)
                PythonLoggingLevel = TargetAccount.ExtraInfoProp[PARAMS_PYTHON_LOGGING_LEVEL];
            LogField(nameof(PythonExePath), PythonExePath);
            LogField(nameof(PythonScriptPath), PythonScriptPath);
            LogField(nameof(PythonLoggingLevel), PythonLoggingLevel);
            if (!File.Exists(PythonExePath))
                throw new FileNotFoundException($"{PARAMS_PYTHON_EXE_PATH}: '{PythonExePath}' not found");
            if (!File.Exists(PythonScriptPath))
                throw new FileNotFoundException($"{PARAMS_PYTHON_SCRIPT_PATH}: '{PythonScriptPath}' not found");
        }

        private void GetAccounts()
        {
            if (TargetAccount?.AccountProp?.ContainsKey(PROPERTIES_USERNAME) == true)
                TargetUsername = TargetAccount.AccountProp[PROPERTIES_USERNAME];
            if (TargetAccount?.AccountProp?.ContainsKey(PROPERTIES_ADDRESS) == true)
                TargetAddress = TargetAccount.AccountProp[PROPERTIES_ADDRESS];
            if (TargetAccount?.AccountProp?.ContainsKey(PROPERTIES_PORT) == true)
                TargetPort = TargetAccount.AccountProp[PROPERTIES_PORT];
            if (LogOnAccount?.AccountProp?.ContainsKey(PROPERTIES_USERNAME) == true)
                LogonUsername = LogOnAccount.AccountProp[PROPERTIES_USERNAME];
            if (ReconcileAccount?.AccountProp?.ContainsKey(PROPERTIES_USERNAME) == true)
                ReconcileUsername = ReconcileAccount.AccountProp[PROPERTIES_USERNAME];
            if (TargetAccount?.CurrentPassword != null)
                TargetCurrentPassword = Crypto.Encrypt(TargetAccount.CurrentPassword);
            if (LogOnAccount?.CurrentPassword != null)
                LogonCurrentPassword = Crypto.Encrypt(LogOnAccount.CurrentPassword);
            if (ReconcileAccount?.CurrentPassword != null)
                ReconcileCurrentPassword = Crypto.Encrypt(ReconcileAccount.CurrentPassword);
            if (RequiresNewPassword)
            {
                if (TargetAccount?.NewPassword == null)
                {
                    throw new InvalidOperationException("Required new password is 'null'");
                }
                TargetNewPassword = Crypto.Encrypt(TargetAccount.NewPassword);
            }
            LogField(nameof(TargetUsername), TargetUsername);
            LogField(nameof(TargetAddress), TargetAddress);
            LogField(nameof(TargetPort), TargetPort);
            LogField(nameof(LogonUsername), LogonUsername);
            LogField(nameof(ReconcileUsername), ReconcileUsername);
            LogField(nameof(TargetCurrentPassword), TargetCurrentPassword);
            LogField(nameof(LogonCurrentPassword), LogonCurrentPassword);
            LogField(nameof(ReconcileCurrentPassword), ReconcileCurrentPassword);
            LogField(nameof(TargetNewPassword), TargetNewPassword);
        }

        private void RunScript(string action)
        {
            var args = EnvHandler.GetArgs(
                action,
                TargetUsername,
                TargetAddress,
                TargetPort,
                LogonUsername,
                ReconcileUsername,
                PythonLoggingLevel);
            var secrets = EnvHandler.GetSecrets(
                TargetCurrentPassword,
                LogonCurrentPassword,
                ReconcileCurrentPassword,
                TargetNewPassword);
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
            foreach (var arg in args)
            {
                LogEnvVar(arg.Key, arg.Value);
                process.StartInfo.EnvironmentVariables[arg.Key] = arg.Value;
            }
            foreach (var secret in secrets)
            {
                LogEnvVar(secret.Key, secret.Value);
                process.StartInfo.EnvironmentVariables[secret.Key] = secret.Value.Secret;
            }
            Logger.WriteLine($"Executing: {PythonExePath} {PythonScriptPath}", LogLevel.INFO);
            process.Start();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            string message = $"Python closed with exit code: {process.ExitCode}";
            if (process.ExitCode != PYTHON_CLOSE_SUCCESS)
            {
                Logger.WriteLine(message, LogLevel.ERROR);
                if (!string.IsNullOrWhiteSpace(stderr))
                {
                    Logger.WriteLine($"StdErr Output: {stderr}", LogLevel.ERROR);
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
                GetAccounts();
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
            platformOutput.Message = ex.Message;
            Logger.WriteLine($"{ex.GetType()}: {ex.Message}", LogLevel.ERROR);
            if (unrecoverable)
            {
                Logger.WriteLine("Closing with failed unrecoverable", LogLevel.ERROR);
                return CLOSE_FAILED_UNRECOVERABLE;
            }
            Logger.WriteLine("Closing with failed recoverable", LogLevel.ERROR);
            return CLOSE_FAILED_RECOVERABLE;
        }
    }
}
