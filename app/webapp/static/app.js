let editingDepositId = null;

const tg = window.Telegram.WebApp;

alert(JSON.stringify({
    initData: tg.initData,
    initDataUnsafe: tg.initDataUnsafe,
    version: tg.version,
    platform: tg.platform
}, null, 2));

alert(
    tg.initData.length
);

tg.expand();

let TELEGRAM_ID =
    tg.initDataUnsafe?.user?.id;

if (!TELEGRAM_ID) {

    TELEGRAM_ID = 123456789;

    console.log(
        "DEV MODE",
        TELEGRAM_ID
    );
}

document.documentElement.style.setProperty(
    "--bg-color",
    tg.themeParams.bg_color || "#ffffff"
);

document.documentElement.style.setProperty(
    "--text-color",
    tg.themeParams.text_color || "#000000"
);

document
    .getElementById("showFormBtn")
    .addEventListener("click", () => {

        document
            .getElementById("depositForm")
            .style.display = "block";
    });

fetch(`/api/summary/${TELEGRAM_ID}`)
    .then(r => r.json())
    .then(data => {

        document.getElementById(
            "totalAmount"
        ).innerText =
            data.total_amount.toLocaleString()
            + " ₽";

        document.getElementById(
            "totalIncome"
        ).innerText =
            data.total_income.toLocaleString()
            + " ₽";
    });


document.getElementById("depositsCount").innerText = data.count;

fetch(`/api/deposits/${TELEGRAM_ID}`)
    .then(r => r.json())
    .then(data => {

        const portfolio = {};

        data.forEach(dep => {
            portfolio[dep.bank] =
                (portfolio[dep.bank] || 0) + Number(dep.amount);
        });

        const total = Object.values(portfolio).reduce((a, b) => a + b, 0);

        const container =
            document.getElementById("portfolio");

        container.innerHTML = "";

        Object.entries(portfolio).forEach(([bank, amount]) => {

            const percent = Math.round((amount / total) * 100);

            const div = document.createElement("div");

            div.className = "portfolio-item";

            div.innerHTML = `
                <div class="bank">${bank}</div>
                <div class="bar">
                    <div class="fill" style="width:${percent}%"></div>
                </div>
                <div class="percent">${percent}%</div>
            `;

            container.appendChild(div);
        });
    });


fetch(`/api/deposits/${TELEGRAM_ID}`)
    .then(r => r.json())
    .then(data => {

        const container =
            document.getElementById("deposits");

        data.forEach(dep => {

            const card =
                document.createElement("div");

            card.className = "card";

            card.innerHTML = `
                <div class="bank">
                    🏦 ${dep.bank}
                </div>
                
                <div class="deposit-name">
                    ${dep.deposit_name}
                </div>
                
                <div class="amount">
                    ${Number(dep.amount)
                        .toLocaleString()} ₽
                </div>
                
                <div class="rate">
                    ${dep.rate}% годовых
                </div>
                
                <div class="months">
                    ${dep.months} мес.
                </div>
                
                <div class="actions">
                
                    <button
                        class="edit-btn"
                        onclick="editDeposit(${dep.id})">
                
                        ✏️
                    </button>
                
                    <button
                        class="delete-btn"
                        onclick="deleteDeposit(${dep.id})">
                
                        🗑️
                    </button>
                
                </div>
                `;

            container.appendChild(card);
        });
    });

async function editDeposit(id) {

    const response =
        await fetch(
            `/api/deposit/${id}`
        );

    const dep =
        await response.json();

    editingDepositId = id;

    document
        .getElementById("depositForm")
        .style.display = "block";

    document
        .getElementById("bank")
        .value = dep.bank;

    document
        .getElementById("depositName")
        .value = dep.deposit_name;

    document
        .getElementById("amount")
        .value = dep.amount;

    document
        .getElementById("rate")
        .value = dep.rate;

    document
        .getElementById("months")
        .value = dep.months;

    document
        .getElementById("capitalization")
        .checked =
            dep.capitalization;
}

if (editingDepositId) {
    // позже будет PUT
}

document
    .getElementById("saveDepositBtn")
    .addEventListener("click", async () => {

        const payload = {

            user_id: TELEGRAM_ID,

            bank:
                document.getElementById(
                    "bank"
                ).value,

            deposit_name:
                document.getElementById(
                    "depositName"
                ).value,

            amount:
                Number(
                    document.getElementById(
                        "amount"
                    ).value
                ),

            rate:
                Number(
                    document.getElementById(
                        "rate"
                    ).value
                ),

            months:
                Number(
                    document.getElementById(
                        "months"
                    ).value
                ),

            capitalization:
                document.getElementById(
                    "capitalization"
                ).checked
        };

        let response;

        if (editingDepositId) {

            response =
                await fetch(
                    `/api/deposits/${editingDepositId}`,
                    {
                        method: "PUT",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(payload)
                    }
                );

        } else {

            response =
                await fetch(
                    "/api/deposits",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(payload)
                    }
                );
        }

        const result =
            await response.json();

        if (result.success) {

            alert(
                "Вклад сохранён"
            );

            location.reload();
        }
    });


async function deleteDeposit(id) {

    const ok = confirm(
        "Удалить вклад?"
    );

    if (!ok) return;

    const response =
        await fetch(
            `/api/deposits/${id}`,
            {
                method: "DELETE"
            }
        );

    const result =
        await response.json();

    if (result.success) {

        location.reload();
    }
}
