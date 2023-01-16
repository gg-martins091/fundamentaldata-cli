import * as commander from "commander";
import figlet from "figlet";
import { loadCompanies } from "./commands/load-companies";
import { Client } from "pg";

console.log(figlet.textSync("Fundamentals"));

const pgr = new commander.Command();

const options = pgr.opts();

pgr.addOption(
  new commander.Option(
    "-v [verboselevel]",
    "0 - NONE; 1 - INFO; 2 - WARNING; 3 - ERROR"
  ).choices(["0", "1", "2", "3"])
);

pgr.addCommand(
  new commander.Command("load-companies")
    .description("Carrega as informações básicas das companhias")
    .action((...args) => loadCompanies(options, args))
);

pgr.addCommand(
  new commander.Command("get-info")
    .description("Pega as informações do ticker")
    .addArgument(
      new commander.Argument("<ticker>", "Ticker da ação da empresa")
    )
    .addArgument(
      new commander.Argument(
        "<info type>",
        "Tipo da informação a ser resgatada"
      ).choices(["balances", "incomes", "cashflows", "marketratios", "ratios"])
    )
    .action((ticker, infoType) => {
      console.log(ticker, infoType);
    })
);

pgr
  .version("0.0.1")
  .description(
    "CLI para resgate e armazenamento de informações das APIs do dadosdemercado.com.br e posterior análise"
  )
  .parse(process.argv);

// const options = pgr.opts();
// declare global {
//   var verboseLevel: number;
// }

// console.log(options);

// if (!!options.verbose) {
//   globalThis.verboseLevel = VerboseLevel.NONE;
// } else {
//   globalThis.verboseLevel = parseInt(options.verbose);
// }
