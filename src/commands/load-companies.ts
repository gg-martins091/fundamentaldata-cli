import { OptionValues } from "commander";
import { getCompanies, upsertCompanies } from "../modules/companies";

import { log, VerboseLevel } from "../services/verbose";

export const loadCompanies = async (opts: OptionValues, ..._: any[]) => {
  log("Resgatando companhias", VerboseLevel.INFO);

  const companies = await getCompanies();

  log("Resgate de companhias finalizado", VerboseLevel.NONE);

  await upsertCompanies(companies);
};
