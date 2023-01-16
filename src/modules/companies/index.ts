import api from "../../services/http";
import db from "../../services/pg";
import { log, VerboseLevel } from "../../services/verbose";

interface Company {
  name: string;
  trade_name: string;
  cvm_code: number;
  cnpj: string;
  founding_date: string;
  main_activity: string;
  website: string;
  controlling_interest: string;
  is_state_owned: boolean;
  is_foreign: boolean;
  is_b3_listed: boolean;
  b3_issuer_code: string;
  b3_listing_segment: string;
  b3_sector: string;
  b3_subsector: string;
  b3_segment: string;
}

interface Ticker {
  ticker: string;
  type: string;
  market_type: string;
  market: string;
  issuer_code: string;
  currency: string;
  isin: string;
}

export const getCompanies = async (): Promise<Company[]> => {
  try {
    const ret = await api.get(`/companies`);
    return ret.data;
  } catch (e) {
    console.log(e);
  }

  return [];
};

export const getTickers = async (cvmCode: string): Promise<Ticker[]> => {
  try {
    const ret = await api.get(`/companies/${cvmCode}/tickers`);
    return ret.data;
  } catch (e) {
    console.log(e);
  }

  return [];
};

export const upsertCompanies = async (companies: Company[]) => {
  try {
    const c = await db.getClient();
    const tmp = `tmp_${(Math.random() + 1).toString(36).substring(7)}`;
    log(`Schema temporário upsertCompanies: ${tmp}`, VerboseLevel.INFO);

    try {
      await c.query("BEGIN");
      await c.query(`CREATE SCHEMA ${tmp}`);

      await c.query(
        `CREATE TABLE ${tmp}.companies (LIKE public.companies INCLUDING ALL)`
      );

      for (const company of companies) {
        if (company.cnpj != null) {
          await c.query(
            `INSERT INTO ${tmp}.companies (name, trade_name,  cvm_code, cnpj, founding_date, main_activity, website, controlling_interest, is_state_owned, is_foreign, is_b3_listed, b3_issuer_code, b3_listing_segment, b3_sector, b3_subsector, b3_segment) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)`,
            [
              company.name,
              company.trade_name,
              company.cvm_code,
              company.cnpj,
              company.founding_date,
              company.main_activity,
              company.website,
              company.controlling_interest,
              company.is_state_owned,
              company.is_foreign,
              company.is_b3_listed,
              company.b3_issuer_code,
              company.b3_listing_segment,
              company.b3_sector,
              company.b3_subsector,
              company.b3_segment,
            ]
          );
        }
      }

      await c.query(
        `INSERT INTO public.companies (name, trade_name,  cvm_code, cnpj, founding_date, main_activity, website, controlling_interest, is_state_owned, is_foreign, is_b3_listed, b3_issuer_code, b3_listing_segment, b3_sector, b3_subsector, b3_segment) 
        SELECT tmp.name, tmp.trade_name, tmp.cvm_code, tmp.cnpj, tmp.founding_date, tmp.main_activity, tmp.website, tmp.controlling_interest, tmp.is_state_owned, tmp.is_foreign, tmp.is_b3_listed, tmp.b3_issuer_code, tmp.b3_listing_segment, tmp.b3_sector, tmp.b3_subsector, tmp.b3_segment
        FROM ${tmp}.companies tmp
        LEFT JOIN public.companies c on c.cvm_code = tmp.cvm_code
        WHERE c.cvm_code isnull`
      );

      await c.query(`DROP SCHEMA ${tmp} CASCADE`);
      await c.query("COMMIT");
    } catch (e) {
      await c.query("ROLLBACK");
      throw e;
    } finally {
      c.end();
    }
  } catch (erro) {
    console.log(erro);
  }
};
