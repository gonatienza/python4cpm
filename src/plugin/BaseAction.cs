using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using CyberArk.Extensions.Plugins.Models;
using CyberArk.Extensions.Utilties.Logger;

namespace CyberArk.Extensions.Plugin.Python4CPM
{
    public abstract class BaseAction : AbsAction
    {
        public const int PythonCloseFailedUnrecoverable = 89;
        public const int PythonCloseFailedRecoverable = 81;
        private const int PythonCloseSuccess = 10;
        private const int CloseSuccess = 0;
        private const int CloseFailedUnrecoverable = 8900;
        private const int CloseFailedRecoverable = 8100;
        private const string PythonExePathParam = "PythonExePath";
        private const string PythonScriptPathParam = "PythonScriptPath";
        private const string PythonLoggingLevelParam = "PythonLoggingLevel";
        private const string PolicyIdProperty = "policyid";
        private const string SafeNameProperty = "safename";
        private const string ObjectNameProperty = "objectname";
        private const string UsernameProperty = "username";
        private const string AddressProperty = "address";
        private const string PortProperty = "port";
        private string _pythonExePath;
        private string _pythonScriptPath;
        private string _pythonLoggingLevel;
        private string _targetPolicyId;
        private string _targetSafeName;
        private string _targetObjectName;
        private string _targetUsername;
        private string _targetAddress;
        private string _targetPort;
        private string _logonUsername;
        private string _reconcileUsername;
        private Password _targetCurrentPassword;
        private Password _logonCurrentPassword;
        private Password _reconcileCurrentPassword;
        private NewPassword _targetNewPassword;

        public BaseAction(List<IAccount> accountList, ILogger logger)
            : base(accountList, logger)
        {
        }

        protected abstract bool RequiresNewPassword { get; }

        protected int RunAction(string action, ref PlatformOutput platformOutput)
        {
            Logger.WriteLine($"Running action: {action}", LogLevel.INFO);
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
                return CloseSuccess;
            }
            catch (PythonExecutionException ex)
            {
                if (ex.ExitCode == PythonCloseFailedRecoverable)
                    return HandleException(ex, false, ref platformOutput);
                return HandleException(ex, true, ref platformOutput);
            }
            catch (Exception ex)
            {
                return HandleException(ex, true, ref platformOutput);
            }
        }

        private string GetLoggingValue(object obj)
        {
            if (obj == null)
                return "[NOT SET]";
            if (obj is Secret)
                return $"{obj}";
            return $"'{obj}'";
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
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PythonExePathParam) == true)
                _pythonExePath = TargetAccount.ExtraInfoProp[PythonExePathParam];
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PythonScriptPathParam) == true)
                _pythonScriptPath = TargetAccount.ExtraInfoProp[PythonScriptPathParam];
            if (TargetAccount?.ExtraInfoProp?.ContainsKey(PythonLoggingLevelParam) == true)
                _pythonLoggingLevel = TargetAccount.ExtraInfoProp[PythonLoggingLevelParam];
            LogField(nameof(_pythonExePath), _pythonExePath);
            LogField(nameof(_pythonScriptPath), _pythonScriptPath);
            LogField(nameof(_pythonLoggingLevel), _pythonLoggingLevel);
            if (!File.Exists(_pythonExePath))
                throw new FileNotFoundException($"{PythonExePathParam}: '{_pythonExePath}' not found");
            if (!File.Exists(_pythonScriptPath))
                throw new FileNotFoundException($"{PythonScriptPathParam}: '{_pythonScriptPath}' not found");
        }

        private void GetAccounts()
        {
            if (TargetAccount?.AccountProp?.ContainsKey(PolicyIdProperty) == true)
                _targetPolicyId = TargetAccount.AccountProp[PolicyIdProperty];
            if (TargetAccount?.AccountProp?.ContainsKey(SafeNameProperty) == true)
                _targetSafeName = TargetAccount.AccountProp[SafeNameProperty];
            if (TargetAccount?.AccountProp?.ContainsKey(ObjectNameProperty) == true)
                _targetObjectName = TargetAccount.AccountProp[ObjectNameProperty];
            if (TargetAccount?.AccountProp?.ContainsKey(UsernameProperty) == true)
                _targetUsername = TargetAccount.AccountProp[UsernameProperty];
            if (TargetAccount?.AccountProp?.ContainsKey(AddressProperty) == true)
                _targetAddress = TargetAccount.AccountProp[AddressProperty];
            if (TargetAccount?.AccountProp?.ContainsKey(PortProperty) == true)
                _targetPort = TargetAccount.AccountProp[PortProperty];
            if (LogOnAccount?.AccountProp?.ContainsKey(UsernameProperty) == true)
                _logonUsername = LogOnAccount.AccountProp[UsernameProperty];
            if (ReconcileAccount?.AccountProp?.ContainsKey(UsernameProperty) == true)
                _reconcileUsername = ReconcileAccount.AccountProp[UsernameProperty];
            if (TargetAccount?.CurrentPassword?.Length > 0)
                _targetCurrentPassword = Password.FromSecureString(TargetAccount.CurrentPassword);
            if (LogOnAccount?.CurrentPassword?.Length > 0)
                _logonCurrentPassword = Password.FromSecureString(LogOnAccount.CurrentPassword);
            if (ReconcileAccount?.CurrentPassword?.Length > 0)
                _reconcileCurrentPassword = Password.FromSecureString(ReconcileAccount.CurrentPassword);
            if (RequiresNewPassword && TargetAccount?.NewPassword?.Length > 0)
                _targetNewPassword = NewPassword.FromSecureString(TargetAccount.NewPassword);
            LogField(nameof(_targetPolicyId), _targetPolicyId);
            LogField(nameof(_targetSafeName), _targetSafeName);
            LogField(nameof(_targetObjectName), _targetObjectName);
            LogField(nameof(_targetUsername), _targetUsername);
            LogField(nameof(_targetAddress), _targetAddress);
            LogField(nameof(_targetPort), _targetPort);
            LogField(nameof(_logonUsername), _logonUsername);
            LogField(nameof(_reconcileUsername), _reconcileUsername);
            LogField(nameof(_targetCurrentPassword), _targetCurrentPassword);
            LogField(nameof(_logonCurrentPassword), _logonCurrentPassword);
            LogField(nameof(_reconcileCurrentPassword), _reconcileCurrentPassword);
            LogField(nameof(_targetNewPassword), _targetNewPassword);
        }

        private void RunScript(string action)
        {
            var args = EnvHandler.GetArgs(
                action,
                _targetPolicyId,
                _targetSafeName,
                _targetObjectName,
                _targetUsername,
                _targetAddress,
                _targetPort,
                _logonUsername,
                _reconcileUsername,
                _pythonLoggingLevel);
            var secrets = EnvHandler.GetSecrets(
                _targetCurrentPassword,
                _logonCurrentPassword,
                _reconcileCurrentPassword,
                _targetNewPassword);
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = _pythonExePath,
                    Arguments = $"\"{_pythonScriptPath}\"",
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
                process.StartInfo.EnvironmentVariables[secret.Key] = secret.Value.Value;
            }
            Logger.WriteLine($"Executing: {_pythonExePath} {_pythonScriptPath}", LogLevel.INFO);
            process.Start();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            string message = $"Python closed with exit code: {process.ExitCode}";
            if (process.ExitCode != PythonCloseSuccess)
            {
                Logger.WriteLine(message, LogLevel.ERROR);
                if (!string.IsNullOrWhiteSpace(stderr))
                    Logger.WriteLine($"StdErr Output: {stderr}", LogLevel.ERROR);
                throw new PythonExecutionException(process.ExitCode);
            }
            Logger.WriteLine(message, LogLevel.INFO);
        }

        private int HandleException(Exception ex, bool unrecoverable, ref PlatformOutput platformOutput)
        {
            platformOutput.Message = ex.Message;
            Logger.WriteLine($"{ex.GetType()}: {ex.Message}", LogLevel.ERROR);
            if (unrecoverable)
            {
                Logger.WriteLine("Closing with failed unrecoverable", LogLevel.ERROR);
                return CloseFailedUnrecoverable;
            }
            Logger.WriteLine("Closing with failed recoverable", LogLevel.ERROR);
            return CloseFailedRecoverable;
        }
    }
}
