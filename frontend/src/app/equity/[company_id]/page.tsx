import { getEquity } from "@/lib/api";
import CompanyHeader from "@/components/equity/CompanyHeader";
import CompanyTabs from "@/components/equity/CompanyTabs";

interface Props {
  params: Promise<{ company_id: string }>;
}

export default async function EquityPage({ params }: Props) {
  const { company_id } = await params;
  const id = Number(company_id);

  const [details, lastPrice] = await Promise.allSettled([
    getEquity("company_details", id),
    getEquity("last_price", id),
  ]);

  const detailsData = details.status === "fulfilled" ? details.value : null;
  const priceData = lastPrice.status === "fulfilled" ? lastPrice.value : null;

  return (
    <div className="space-y-6">
      <CompanyHeader companyId={id} details={detailsData} price={priceData} />
      <CompanyTabs companyId={id} />
    </div>
  );
}
