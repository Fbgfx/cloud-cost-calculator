import streamlit as st

st.set_page_config(page_title="Cloud Cost Estimator", page_icon="☁️")

st.title("☁️ Cloud Cost Estimator & Migration Advisor")

st.write(
    "Estimate monthly cloud costs for common compute, storage, and database workloads "
    "on AWS and Azure. This demo uses sample public pricing — always verify exact prices "
    "from each cloud provider."
)

PROVIDERS = ["AWS", "Azure"]

SERVICES = {
    "Compute (VMs / EC2)": {
        "AWS": {
            "t3.micro (US-East-1)": 0.0104,  # $/hour
            "t3.small (US-East-1)": 0.0208,
        },
        "Azure": {
            "B1s (East US)": 0.012,   # $/hour
            "B2s (East US)": 0.024,
        },
        "unit": "per hour",
    },
    "Object Storage (S3 / Blob)": {
        "AWS": {
            "S3 Standard (US-East-1)": 0.023,  # $/GB-month
            "S3 Infrequent Access": 0.0125,
        },
        "Azure": {
            "Blob Hot (LRS)": 0.0184,  # $/GB-month
            "Blob Cool (LRS)": 0.01,
        },
        "unit": "per GB-month",
    },
    "Managed Database (RDS / Azure SQL)": {
        "AWS": {
            "RDS t3.micro (Multi-AZ)": 0.034,  # $/hour (approx)
        },
        "Azure": {
            "Azure SQL Basic": 0.021,  # $/hour (approx)
        },
        "unit": "per hour",
    },
}


def compute_cost(service_category, provider, option, usage_amount):
    price = SERVICES[service_category][provider][option]
    return price * usage_amount


with st.sidebar:
    st.header("Configuration")
    provider = st.selectbox("Cloud provider", PROVIDERS)
    service_category = st.selectbox("Service category", list(SERVICES.keys()))

    options = list(SERVICES[service_category][provider].keys())
    option = st.selectbox("Service option", options)

    unit = SERVICES[service_category]["unit"]
    if "hour" in unit:
        usage_label = "Estimated hours per month"
        default_usage = 730  # 24/7
    else:
        usage_label = "Estimated storage (GB) per month"
        default_usage = 100

    usage_amount = st.number_input(
        usage_label,
        min_value=0.0,
        value=float(default_usage),
        step=1.0,
    )

    st.markdown("---")
    st.caption("💡 Tip: These are sample prices. For production workloads, pull live prices from AWS/Azure pricing APIs.")

if usage_amount <= 0:
    st.warning("Enter a usage amount greater than 0 to estimate costs.")
else:
    monthly_cost = compute_cost(service_category, provider, option, usage_amount)
    st.subheader("📊 Cost Estimate")

    st.metric(
        label=f"Estimated monthly cost on {provider}",
        value=f"${monthly_cost:,.2f}",
        help=f"{option} at given usage",
    )

    st.write("#### Breakdown")
    st.write(f"- **Provider:** {provider}")
    st.write(f"- **Service category:** {service_category}")
    st.write(f"- **Option:** {option}")
    st.write(
        f"- **Unit price:** "
        f"${SERVICES[service_category][provider][option]:.4f} {SERVICES[service_category]['unit']}"
    )
    st.write(
        f"- **Usage:** {usage_amount:,.0f} "
        f"{SERVICES[service_category]['unit'].split('per ')[-1]}"
    )
    st.write(f"- **Estimated monthly cost:** `${monthly_cost:,.2f}`")

    st.write("#### Simple Migration & Optimization Advice")

    advice = []

    if service_category == "Compute (VMs / EC2)":
        if usage_amount >= 730:
            advice.append(
                "- This workload looks like it's running **24/7**. "
                "Consider reserved instances, savings plans, or Azure reserved VMs."
            )
        else:
            advice.append(
                "- Since usage is **not 24/7**, consider **auto-scaling** or **serverless** "
                "(AWS Lambda / Azure Functions)."
            )
        advice.append(
            "- Right-size the instance based on real CPU & memory metrics. Oversized VMs waste money."
        )

    elif service_category == "Object Storage (S3 / Blob)":
        if usage_amount > 500:
            advice.append(
                "- For large storage footprints, consider tiering: move infrequently accessed data to "
                "**S3 IA / Glacier** or **Blob Cool / Archive**."
            )
        else:
            advice.append(
                "- For smaller datasets, staying on **standard tiers** may be simplest while you grow."
            )
        advice.append(
            "- Enable lifecycle policies to automatically move older objects to cheaper tiers."
        )

    elif service_category == "Managed Database (RDS / Azure SQL)":
        advice.append(
            "- Consider whether you really need **high availability / Multi-AZ** for non-critical workloads."
        )
        advice.append(
            "- Scale down during off-hours or explore **serverless database options** where available."
        )

    if provider == "AWS":
        advice.append(
            "- Use the **AWS Pricing Calculator** and **Cost Explorer** for more precise multi-service estimates."
        )
    else:
        advice.append(
            "- Use the **Azure Pricing Calculator** and **Cost Management + Billing** for detailed estimates."
        )

    for a in advice:
        st.write(a)
