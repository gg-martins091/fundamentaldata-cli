import api from "../../services/http";

export const getBalances = async (cvm_code: number) => {
  const ret = await api.get(`/companies/${cvm_code}/balances`);

  console.log(ret);
};
