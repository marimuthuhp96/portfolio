/* ============================================================
   Mari Muthu Portfolio — charts.js
   All Chart.js configurations: Radar, Bar, Doughnut
   ============================================================ */

'use strict';

/* Shared Chart.js defaults */
if (typeof Chart !== 'undefined') {
  Chart.defaults.color             = '#A1A1AA';
  Chart.defaults.font.family       = "'Inter', sans-serif";
  Chart.defaults.font.size         = 12;
  Chart.defaults.plugins.legend.labels.padding = 20;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(24,24,27,0.95)';
  Chart.defaults.plugins.tooltip.borderColor     = 'rgba(59,130,246,0.3)';
  Chart.defaults.plugins.tooltip.borderWidth     = 1;
  Chart.defaults.plugins.tooltip.padding         = 12;
  Chart.defaults.plugins.tooltip.titleColor      = '#FFFFFF';
  Chart.defaults.plugins.tooltip.bodyColor       = '#A1A1AA';
  Chart.defaults.plugins.tooltip.cornerRadius    = 10;
}

/* ── Radar Chart (Skills Overview) ───────────────────────── */
function initRadarChart() {
  const canvas = document.getElementById('radar-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['SQL', 'Python', 'Power BI', 'Excel', 'Machine Learning', 'Statistics', 'Data Viz', 'DAX'],
      datasets: [{
        label: 'Skill Level',
        data: [90, 82, 88, 92, 72, 80, 85, 78],
        fill: true,
        backgroundColor: 'rgba(59,130,246,0.12)',
        borderColor:     '#3B82F6',
        borderWidth:     2,
        pointBackgroundColor: '#3B82F6',
        pointBorderColor:     '#fff',
        pointBorderWidth:     2,
        pointRadius:          5,
        pointHoverRadius:     7,
        pointHoverBackgroundColor: '#60A5FA',
      }, {
        label: 'Industry Avg',
        data: [70, 65, 65, 70, 60, 65, 68, 60],
        fill: true,
        backgroundColor: 'rgba(139,92,246,0.06)',
        borderColor:     'rgba(139,92,246,0.4)',
        borderWidth:     1.5,
        borderDash:      [4, 4],
        pointBackgroundColor: '#8B5CF6',
        pointBorderColor:     '#fff',
        pointBorderWidth:     2,
        pointRadius:          4,
        pointHoverRadius:     6,
      }],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min:   0,
          max:   100,
          ticks: {
            stepSize:    20,
            display:     false,
          },
          grid: {
            color:     'rgba(255,255,255,0.06)',
            lineWidth: 1,
          },
          pointLabels: {
            font:  { size: 11, weight: '600' },
            color: '#A1A1AA',
            padding: 8,
          },
          angleLines: { color: 'rgba(255,255,255,0.05)' },
        },
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels:   { usePointStyle: true, pointStyleWidth: 10, padding: 24 },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.r}%`,
          },
        },
      },
    },
  });
}

/* ── Bar Chart (Proficiency by Tool) ─────────────────────── */
function initBarChart() {
  const canvas = document.getElementById('bar-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0,   'rgba(59,130,246,0.9)');
  gradient.addColorStop(1,   'rgba(139,92,246,0.5)');

  const gradientGreen = ctx.createLinearGradient(0, 0, 0, 300);
  gradientGreen.addColorStop(0, 'rgba(16,185,129,0.9)');
  gradientGreen.addColorStop(1, 'rgba(5,150,105,0.5)');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Advanced\nExcel', 'SQL', 'Python', 'Power BI', 'DAX', 'Power\nQuery', 'ML', 'Git'],
      datasets: [{
        label: 'Proficiency',
        data:  [92, 90, 82, 88, 78, 85, 72, 75],
        backgroundColor: [
          gradient, gradient, gradient, gradientGreen,
          gradient, gradientGreen, gradient, gradient,
        ],
        borderRadius:       8,
        borderSkipped:      false,
        borderWidth:        0,
        hoverBackgroundColor: 'rgba(59,130,246,0.95)',
      }],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          min:  0,
          max:  100,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            callback: (v) => v + '%',
            font: { size: 11 },
          },
        },
        y: {
          grid: { display: false },
          ticks: { font: { size: 11, weight: '600' } },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.x}% Proficiency`,
          },
        },
      },
    },
  });
}

/* ── Doughnut Chart (Tools Category) ─────────────────────── */
function initDoughnutChart() {
  const canvas = document.getElementById('doughnut-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Data Analysis', 'Visualization', 'Machine Learning', 'Business Intelligence', 'Programming'],
      datasets: [{
        data:            [30, 25, 15, 20, 10],
        backgroundColor: [
          'rgba(59,130,246,0.85)',
          'rgba(16,185,129,0.85)',
          'rgba(236,72,153,0.85)',
          'rgba(245,158,11,0.85)',
          'rgba(139,92,246,0.85)',
        ],
        borderColor:     'rgba(24,24,27,0.9)',
        borderWidth:     3,
        hoverBorderWidth: 4,
        hoverOffset:     6,
      }],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      cutout:              '68%',
      plugins: {
        legend: {
          position: 'right',
          labels:   {
            usePointStyle: true,
            pointStyleWidth: 10,
            padding: 16,
            font: { size: 11 },
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.parsed}%`,
          },
        },
      },
    },
  });
}

/* ── Projects Timeline Chart (Line) ──────────────────────── */
function initTimelineChart() {
  const canvas = document.getElementById('timeline-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  const ctx = canvas.getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, 0, 200);
  grad.addColorStop(0,   'rgba(59,130,246,0.3)');
  grad.addColorStop(1,   'rgba(59,130,246,0)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['2022', 'Q1 2023', 'Q3 2023', 'Q1 2024', 'Q3 2024', 'Q1 2025', 'Q3 2025', '2026'],
      datasets: [{
        label: 'Skills Progress',
        data:  [10, 25, 40, 52, 65, 75, 85, 95],
        fill:       true,
        backgroundColor: grad,
        borderColor:     '#3B82F6',
        borderWidth:     2.5,
        pointBackgroundColor: '#3B82F6',
        pointBorderColor:     '#09090B',
        pointBorderWidth:     3,
        pointRadius:          6,
        tension:        0.45,
        pointHoverRadius: 8,
      }],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { font: { size: 11 } },
        },
        y: {
          min:  0,
          max:  100,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { callback: (v) => v + '%', font: { size: 11 } },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` Skill Growth: ${ctx.parsed.y}%`,
          },
        },
      },
    },
  });
}

/* ── Init all charts on DOM ready ────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initRadarChart();
  initBarChart();
  initDoughnutChart();
  initTimelineChart();
});
