// Point this to your FastAPI local server
const API_URL = 'https://revops-inference-engines.onrender.com';

// Executive Currency Formatter
const currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
});

// Global state variables
let masterOpportunities = [];
let riskScatterChart = null;

async function initializeTerminal() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error(`Network 500: ${response.status}`);
        
        const payload = await response.json();
        masterOpportunities = payload.opportunities;

        // 1. Calculate the 3-Tier Financial Breakdowns dynamically
        let healthyCount = 0, healthyVal = 0;
        let elevatedCount = 0, elevatedVal = 0;
        let criticalCount = 0, criticalVal = 0;

        masterOpportunities.forEach(deal => {
            if (deal.flight_risk_pct >= 65.0) {
                criticalCount++;
                criticalVal += deal.amount;
            } else if (deal.flight_risk_pct >= 35.0) {
                elevatedCount++;
                elevatedVal += deal.amount;
            } else {
                healthyCount++;
                healthyVal += deal.amount;
            }
        });

        // 2. Paint Top Totals
        document.getElementById('kpi-open-arr').textContent = currencyFormatter.format(payload.metadata.total_open_arr);
        document.getElementById('kpi-active-deals').textContent = payload.metadata.total_active_deals;

        // 3. Paint 3-Tier Cards
        document.getElementById('kpi-healthy-count').textContent = `${healthyCount} Deals`;
        document.getElementById('kpi-healthy-val').textContent = currencyFormatter.format(healthyVal);

        document.getElementById('kpi-elevated-count').textContent = `${elevatedCount} Deals`;
        document.getElementById('kpi-elevated-val').textContent = currencyFormatter.format(elevatedVal);

        document.getElementById('kpi-critical-count').textContent = `${criticalCount} Deals`;
        document.getElementById('kpi-critical-val').textContent = currencyFormatter.format(criticalVal);

        // 4. Render Cards (Top 25 initial view to keep UI snappy)
        renderQueueCards(masterOpportunities.slice(0, 25));

        // 5. Render Interactive Scatter Plot
        renderInferenceChart(masterOpportunities);

        // 6. Hook up the Live Search/Filter bar
        document.getElementById('search-box').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = masterOpportunities.filter(deal => 
                deal.company_name.toLowerCase().includes(term) || deal.deal_name.toLowerCase().includes(term)
            );
            renderQueueCards(filtered.slice(0, 25));
        });

    } catch (error) {
        console.error('Inference Engine Offline:', error);
        
        document.getElementById('status-dot').className = "w-2.5 h-2.5 rounded-full bg-[#ef4444] animate-pulse shadow-[0_0_10px_#ef4444]";
        document.getElementById('status-text').className = "text-[#ef4444] font-mono text-xs uppercase tracking-wider font-semibold";
        document.getElementById('status-text').textContent = "API Offline";
        
        document.getElementById('deals-grid').innerHTML = `
            <div class="col-span-full py-12 text-center text-[#ef4444] font-mono text-xs bg-red-950/10 border border-red-900/50 rounded-xl">
                [ERR_CONNECTION_REFUSED] Failed to handshake with FastAPI microservice at port :8000.
            </div>
        `;
    }
}

function renderQueueCards(opportunities) {
    const gridContainer = document.getElementById('deals-grid');
    gridContainer.innerHTML = '';

    if (opportunities.length === 0) {
        gridContainer.innerHTML = `
            <div class="col-span-full py-8 text-center text-gray-500 font-mono text-xs">
                No matching opportunities found in local buffer.
            </div>
        `;
        return;
    }

    opportunities.forEach((deal) => {
        // --- 3-TIER RISK LOGIC ---
        let riskColor, barColor, borderColor, riskBg;
        
        if (deal.flight_risk_pct >= 65.0) {
            riskColor = 'text-[#ef4444]'; 
            barColor = 'bg-[#ef4444] shadow-[0_0_8px_rgba(239,68,68,0.8)]';
            borderColor = 'border-red-900/30';
            riskBg = 'bg-red-950/30';
        } else if (deal.flight_risk_pct >= 35.0) {
            riskColor = 'text-[#facc15]'; 
            barColor = 'bg-[#facc15] shadow-[0_0_8px_rgba(250,204,21,0.6)]';
            borderColor = 'border-yellow-900/30';
            riskBg = 'bg-yellow-950/30';
        } else {
            riskColor = 'text-[#00ff88]'; 
            barColor = 'bg-[#00ff88] shadow-[0_0_8px_rgba(0,255,136,0.5)]';
            borderColor = 'border-emerald-900/30';
            riskBg = 'bg-emerald-950/30';
        }

        const card = document.createElement('div');
        const cleanId = deal.company_name.replace(/[^a-zA-Z0-9]/g, '');
        card.id = `card-${cleanId}`;
        card.className = `bg-gray-900/60 border ${borderColor} rounded-xl p-5 hover:bg-gray-800 transition-all duration-300 flex flex-col justify-between`;

        card.innerHTML = `
            <div class="mb-4">
                <div class="flex justify-between items-start mb-1">
                    <h3 class="font-semibold text-white truncate pr-2">${deal.company_name}</h3>
                    <span class="bg-[#0a0f0d] border border-gray-700 text-gray-400 px-2 py-0.5 rounded text-[10px] font-mono whitespace-nowrap">
                        ${deal.est_days_left}d left
                    </span>
                </div>
                <p class="text-xs text-gray-500 font-mono truncate">${deal.deal_name}</p>
            </div>

            <div class="space-y-4">
                <div class="p-3 rounded-lg ${riskBg} border ${borderColor} flex justify-between items-center">
                    <p class="text-[10px] text-gray-400 uppercase tracking-wider">Valuation</p>
                    <p class="text-lg font-bold font-mono ${riskColor}">${currencyFormatter.format(deal.amount)}</p>
                </div>

                <div>
                    <div class="flex justify-between items-end mb-1">
                        <p class="text-[10px] text-gray-500 uppercase tracking-wider">AI Churn Vector</p>
                        <span class="${riskColor} font-mono font-bold text-sm">${deal.flight_risk_pct}%</span>
                    </div>
                    <div class="w-full bg-[#0a0f0d] rounded-full h-1.5 overflow-hidden border border-gray-800">
                        <div class="${barColor} h-full rounded-full transition-all duration-500" style="width: ${deal.flight_risk_pct}%"></div>
                    </div>
                </div>
            </div>
        `;
        gridContainer.appendChild(card);
    });
}

function renderInferenceChart(deals) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    
    if (riskScatterChart) riskScatterChart.destroy();

    const plotData = deals.slice(0, 65).map((deal) => {
        const cleanId = deal.company_name.replace(/[^a-zA-Z0-9]/g, '');
        return {
            x: deal.flight_risk_pct,
            y: deal.amount,
            account: deal.company_name,
            days: deal.est_days_left,
            targetCardId: `card-${cleanId}`
        };
    });

    riskScatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                data: plotData,
                backgroundColor: plotData.map(d => {
                    if (d.x >= 65) return 'rgba(239, 68, 68, 0.7)';
                    if (d.x >= 35) return 'rgba(250, 204, 21, 0.7)';
                    return 'rgba(0, 255, 136, 0.6)';
                }),
                borderColor: plotData.map(d => {
                    if (d.x >= 65) return '#ef4444';
                    if (d.x >= 35) return '#facc15';
                    return '#00ff88';
                }),
                borderWidth: 1.5,
                pointRadius: 5,
                pointHoverRadius: 9,
                pointHoverBackgroundColor: '#ffffff',
                pointHoverBorderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0a0f0d',
                    titleColor: '#ffffff',
                    bodyColor: '#9ca3af',
                    borderColor: '#1f2937',
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 4,
                    callbacks: {
                        label: function(context) {
                            const p = context.raw;
                            return [
                                `Account: ${p.account}`,
                                `Value:   ${currencyFormatter.format(p.y)}`,
                                `Risk:    ${p.x}% (${p.days}d to close)`
                            ];
                        }
                    }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const clickedPoint = plotData[elements[0].index];
                    const cardElem = document.getElementById(clickedPoint.targetCardId);
                    
                    if (cardElem) {
                        cardElem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        
                        // Select the correct ring color based on risk
                        let ringColor = 'ring-[#00ff88]';
                        if(clickedPoint.x >= 65) ringColor = 'ring-[#ef4444]';
                        else if(clickedPoint.x >= 35) ringColor = 'ring-[#facc15]';

                        cardElem.classList.add('ring-2', ringColor, 'bg-gray-800');
                        
                        setTimeout(() => {
                            cardElem.classList.remove('ring-2', ringColor, 'bg-gray-800');
                        }, 2000);
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'AI Churn Probability (%)', color: '#6b7280', font: { size: 10 } },
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    ticks: { color: '#9ca3af', font: { family: 'monospace', size: 10 } }
                },
                y: {
                    title: { display: true, text: 'Deal Valuation ($)', color: '#6b7280', font: { size: 10 } },
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    ticks: {
                        color: '#9ca3af',
                        font: { family: 'monospace', size: 10 },
                        callback: val => `$${val / 1000}k`
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', initializeTerminal);