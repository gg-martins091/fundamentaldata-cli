
drop table tickers;
create table tickers (
	id bigserial,
	ticker text,
type text,
cvm_code bigint,
market_type text,
market text,
issuer_code text,
currency text,
isin text,
	constraint tickers_pkey primary key (id)
);

drop table companies;
create table companies (
	id bigserial,
	name text,
	trade_name text,
	cvm_code bigint,
	cnpj text,
	founding_date text,
	main_activity text,
	website text,
	controlling_interest text,
	is_state_owned boolean,
	is_foreign boolean,
	is_b3_listed boolean,
	b3_issuer_code text,
	b3_listing_segment text,
	b3_sector text,
	b3_subsector text,
	b3_segment text,
	constraint companies_pkey primary key (id)
);

drop table balances;
create table balances (
	id bigserial,
	cvm_code bigint,
statement_type text,
reference_date date,
assets bigint,
current_assets bigint,
cash bigint,
financial_investments bigint,
receivables bigint,
inventories bigint,
biological_assets bigint,
noncurrent_assets bigint,
investments bigint,
fixed_assets bigint,
intangible_assets bigint,
liabilities bigint,
current_liabilities bigint,
suppliers bigint,
loans bigint,
noncurrent_liabilities bigint,
long_term_loans bigint,
equity bigint,
equity_non_controlling bigint,
	constraint balances_pkey primary key (id)
);

drop table incomes;
create table incomes (
	id bigserial,
	cvm_code bigint,
statement_type text,
period_init date,
period_end date,
period_type text,
net_sales bigint,
costs bigint,
gross_income bigint,
operating_expenses bigint,
ebit bigint,
non_operating_income bigint,
profit_before_taxes bigint,
taxes bigint,
continued_operations bigint,
discontinued_operations bigint,
net_income bigint,
net_income_controlling bigint,
net_income_non_controlling bigint,
	constraint incomes_pkey primary key (id)
);

drop table cash_flows;
create table cash_flows (
	id bigserial,
	cvm_code bigint,
statement_type text,
period_init date,
period_end date,
period_type text,
operating bigint,
investing bigint,
financing bigint,
	constraint cash_flows_pkey primary key (id)
);


drop table market_ratios;
create table market_ratios (
	id bigserial,
	cvm_code bigint,
ticker text,
reference_date date,
shares bigint,
price numeric,
earnings_per_share numeric,
equity_per_share numeric,
ebit_per_share numeric,
assets_per_share numeric,
net_sales_per_share numeric,
price_earnings numeric,
price_to_book numeric,
price_to_sales numeric,
price_to_cash_flow numeric,
	constraint market_ratios_pkey primary key (id)
);



drop table ratios;
create table ratios (
	id bigserial,
	cvm_code integer,
statement_type text,
period_init date,
period_end date,
period_type text,
gross_margin numeric,
net_margin numeric,
ebit_margin numeric,
operating_margin numeric,
return_on_equity numeric,
return_on_assets numeric,
asset_turnover numeric,
current_liquidity numeric,
quick_liquidity numeric,
cash_liquidity numeric,
working_capital numeric,
gross_debt numeric,
net_debt numeric,
total_debt numeric,
ebitda numeric,
ebitda_margin numeric,
	constraint ratios_pkey primary key (id)
);

drop table cash_flows;
create table cash_flows (
	id bigserial,
	cvm_code bigint,
	statement_type text,
	period_init date,
	period_end date,
	period_type text,
	operating bigint,
	investing bigint,
	financing bigint,
	constraint cash_flows_pkey primary key (id)
);
