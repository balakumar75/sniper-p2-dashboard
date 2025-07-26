// static/script.js

fetch('/trade_history.json')
  .then(r => r.json())
  .then(runs => {
    // Flatten the array of runs into one list of trades
    const allTrades = runs.flatMap(run =>
      run.trades.map(t => ({ ...t, run_date: run.run_date }))
    );

    const tbody = document.querySelector('#trades-table tbody');
    tbody.innerHTML = allTrades.map(t => `
      <tr data-status="${t.status}" data-type="${t.type}">
        <td>${t.run_date}</td>
        <td>${t.symbol}</td>
        <td>${t.type}</td>
        <td>${t.entry ?? ''}</td>
        <td>${
          t.type === 'Options-Strangle'
            ? `P:${t.put_strike}@${t.put_price} / C:${t.call_strike}@${t.call_price}`
            : ''
        }</td>
        <td>${t.status}</td>
        <td>${t.action}</td>
      </tr>
    `).join('');

    function applyFilters() {
      const status = document.getElementById('filter-status').value;
      const type   = document.getElementById('filter-type').value;
      tbody.querySelectorAll('tr').forEach(row => {
        const okStatus = !status || row.dataset.status === status;
        const okType   = !type   || row.dataset.type === type;
        row.style.display = (okStatus && okType) ? '' : 'none';
      });
    }

    document.getElementById('filter-status').addEventListener('change', applyFilters);
    document.getElementById('filter-type').addEventListener('change', applyFilters);
  });
