import chalk from "chalk";

declare global {
  var verboseLevel: VerboseLevel;
}

export enum VerboseLevel {
  NONE = 0,
  INFO = 1,
  WARNING = 2,
  ERROR = 3,
}

const VerboseLevelText: { [key in VerboseLevel]?: string } = {
  [VerboseLevel.NONE]: "INFO",
  [VerboseLevel.INFO]: "INFO",
  [VerboseLevel.WARNING]: "WARNING",
  [VerboseLevel.ERROR]: "ERROR",
};

const VerboseLevelColor: { [key in VerboseLevel]: string } = {
  [VerboseLevel.NONE]: "#4287F5",
  [VerboseLevel.INFO]: "#4287F5",
  [VerboseLevel.WARNING]: "#f59e42",
  [VerboseLevel.ERROR]: "#f54242",
};

export const log = (logText: string, logLevel = VerboseLevel.NONE) => {
  globalThis.verboseLevel = VerboseLevel.INFO;

  if (globalThis.verboseLevel >= logLevel) {
    const text = `[${new Date().toString().split(" GMT")[0]}] ${chalk.hex(
      VerboseLevelColor[globalThis.verboseLevel]
    )(`(${VerboseLevelText[globalThis.verboseLevel]})`)} ${logText}`;

    console.log(text);
  }
};
