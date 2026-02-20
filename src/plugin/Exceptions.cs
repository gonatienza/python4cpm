using System;

namespace CyberArk.Extensions.Python4CPM
{
    public class PythonExecutionException : Exception
    {
        public int ExitCode { get; }

        public override string Message
        {
            get
            {
                if (ExitCode == BaseAction.PYTHON_CLOSE_FAILED_UNRECOVERABLE)
                    return "Python closed with failed unrecoverable";
                if (ExitCode == BaseAction.PYTHON_CLOSE_FAILED_RECOVERABLE)
                    return "Python closed with failed recoverable";
                else
                    return "Python closed unexpectedly";
            }
        }

        public PythonExecutionException(int exitCode): base()
        {
            ExitCode = exitCode;
        }
    }
}
