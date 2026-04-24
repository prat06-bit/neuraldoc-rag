from __future__ import annotations

import streamlit as st

def render_analytics(
    stats: dict,
    api_ok: bool,
    ready: bool,
    chunks: int,
    files: list[str],
) -> None:

    #  Recent queries rows 
    recent_rows = ""
    for q in stats["recent"]:
        icon = "✕" if q["refused"] else "✓"
        ic = "#E05A6D" if q["refused"] else "#48BB78"
        bg = "rgba(224,90,109,0.06)" if q["refused"] else "rgba(72,187,120,0.06)"
        recent_rows += (
            f'<div style="display:flex;align-items:center;gap:14px;padding:14px 18px;'
            f'border-radius:14px;margin-bottom:8px;background:{bg};'
            f'border:1px solid rgba(45,43,85,0.04);'
            f'transition:transform 0.18s ease,box-shadow 0.18s ease;'
            f'animation:slideUp 0.4s ease both;"'
            f' onmouseover="this.style.transform=\'translateX(4px)\';this.style.boxShadow=\'0 2px 12px rgba(124,92,252,0.08)\'"'
            f' onmouseout="this.style.transform=\'\';this.style.boxShadow=\'none\'">'
            f'<div style="width:22px;height:22px;border-radius:50%;flex-shrink:0;'
            f'background:{ic}18;border:1.5px solid {ic}35;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:10px;font-weight:700;color:{ic};">{icon}</div>'
            f'<span style="flex:1;font-size:13.5px;font-family:\'Inter\',sans-serif;'
            f'color:var(--t1);font-weight:450;">{q["query"][:80]}</span>'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
            f'color:var(--t3);background:rgba(124,92,252,0.06);padding:3px 10px;'
            f'border-radius:var(--rf);border:1px solid rgba(124,92,252,0.08);">{q["latency_ms"]}ms</span>'
            f'</div>'
        )

    ans_pct = round((stats['answered']/stats['total_queries']*100) if stats['total_queries'] else 0)
    ref_pct = round((stats['refused']/stats['total_queries']*100) if stats['total_queries'] else 0)

    #  Card builder helper 
    def metric_card(value, label, color, delay, extra=""):
        return f"""
        <div style="background:#FFFFFF;border:1px solid rgba(45,43,85,0.05);
          border-radius:20px;padding:28px 20px 24px;text-align:center;
          box-shadow:0 1px 4px rgba(45,43,85,0.03),0 4px 24px rgba(124,92,252,0.04);
          animation:slideUp 0.5s ease {delay} both;
          transition:transform 0.22s ease,box-shadow 0.22s ease;"
          onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 32px rgba(124,92,252,0.10)'"
          onmouseout="this.style.transform='';this.style.boxShadow='0 1px 4px rgba(45,43,85,0.03),0 4px 24px rgba(124,92,252,0.04)'">
          <div style="font-family:'Instrument Serif',serif;font-size:38px;color:{color};
            line-height:1;margin-bottom:8px;font-weight:400;
            animation:counterUp 0.6s ease {delay} both;">{value}</div>
          <div style="font-size:10px;font-weight:700;color:var(--t3);
            letter-spacing:0.12em;text-transform:uppercase;font-family:'Inter',sans-serif;">{label}</div>
          {extra}
        </div>"""

    #  Progress bar helper 
    def progress_bar(pct, color):
        return f"""<div style="margin-top:12px;height:3px;border-radius:4px;
          background:rgba(45,43,85,0.05);overflow:hidden;">
          <div style="height:100%;background:{color};border-radius:4px;
            width:{pct}%;transition:width 1.2s cubic-bezier(0.4,0,0.2,1);"></div></div>"""

    #  Render 
    st.html(f"""
    <style>
    /* Analytics page overrides */
    .analytics-wrap {{
      padding: 24px 52px 48px;
      position: relative;
      z-index: 10;
      font-family: 'Inter', 'Plus Jakarta Sans', sans-serif;
    }}
    </style>

    <div class="analytics-wrap">

      <!-- Header -->
      <div style="margin-bottom:28px;animation:slideUp 0.4s ease both;">
        <div style="font-size:11px;font-weight:600;color:var(--v);
          letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;
          font-family:'Inter',sans-serif;">Live Observability</div>
        <div style="font-family:'Instrument Serif',serif;font-size:32px;color:var(--t1);
          font-weight:400;line-height:1.2;">
          Query <em style="font-style:italic;color:var(--v);">Analytics</em></div>
      </div>

      <!--  Metric Cards  -->
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:24px;">

        {metric_card(stats['total_queries'], "Total Queries", "var(--v)", ".05s")}

        {metric_card(stats['answered'], "Answered", "#48BB78", ".1s",
            progress_bar(ans_pct, "#48BB78"))}

        {metric_card(stats['refused'], "Refused", "#E05A6D", ".15s",
            progress_bar(ref_pct, "#E05A6D"))}

        {metric_card(f"{stats['refusal_rate']}%", "Refusal Rate", "#ED8936", ".2s",
            f'<div style="margin-top:10px;font-size:11px;color:var(--t3);font-family:\'Inter\',sans-serif;">{"Good" if stats["refusal_rate"] < 20 else "High — check threshold"}</div>')}

        {metric_card(f"{int(stats['avg_latency_ms'])}ms", "Avg Latency", "#38B2AC", ".25s",
            f'<div style="margin-top:10px;font-size:11px;color:var(--t3);font-family:\'Inter\',sans-serif;">{"Fast" if stats["avg_latency_ms"] < 3000 else "Consider GPU"}</div>')}

      </div>

      <!--  Recent Queries  -->
      <div style="background:#FFFFFF;border:1px solid rgba(45,43,85,0.05);
        border-radius:20px;padding:28px 30px;margin-bottom:20px;
        box-shadow:0 1px 4px rgba(45,43,85,0.03),0 4px 24px rgba(124,92,252,0.04);
        animation:slideUp 0.5s ease .3s both;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
          <div style="font-size:14px;font-weight:600;color:var(--t1);
            font-family:'Inter',sans-serif;">Recent Queries</div>
          <div style="font-size:11px;color:var(--t3);background:var(--s2);
            padding:4px 14px;border-radius:var(--rf);font-weight:500;
            border:1px solid rgba(45,43,85,0.04);font-family:'Inter',sans-serif;">
            Last {len(stats['recent'])} of {stats['total_queries']} total</div>
        </div>
        {'<div style="text-align:center;padding:40px 20px;color:var(--t3);font-size:13.5px;font-family:\'Inter\',sans-serif;line-height:1.8;">No queries recorded yet. Send a message to start tracking.</div>' if not stats['recent'] else recent_rows}
      </div>

      <!-- ═══ Bottom row: Status + MLOps ═══ -->
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px;">

        <!-- System Status -->
        <div style="background:#FFFFFF;border:1px solid rgba(45,43,85,0.05);
          border-radius:20px;padding:24px 28px;
          box-shadow:0 1px 4px rgba(45,43,85,0.03),0 4px 24px rgba(124,92,252,0.04);
          animation:slideUp 0.5s ease .35s both;">
          <div style="font-size:10px;font-weight:700;color:var(--t3);
            letter-spacing:0.1em;text-transform:uppercase;margin-bottom:18px;
            font-family:'Inter',sans-serif;">System Status</div>
          <div style="display:flex;flex-direction:column;gap:14px;">

            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span style="font-size:13.5px;color:var(--t2);font-family:'Inter',sans-serif;">FastAPI Backend</span>
              <span style="font-size:11px;font-weight:600;padding:4px 14px;border-radius:var(--rf);
                {'color:#48BB78;background:rgba(72,187,120,0.08);border:1px solid rgba(72,187,120,0.18);' if api_ok else 'color:#E05A6D;background:rgba(224,90,109,0.08);border:1px solid rgba(224,90,109,0.18);'}
                font-family:'Inter',sans-serif;">
                {'Online' if api_ok else 'Offline'}</span>
            </div>

            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span style="font-size:13.5px;color:var(--t2);font-family:'Inter',sans-serif;">RAG Pipeline</span>
              <span style="font-size:11px;font-weight:600;padding:4px 14px;border-radius:var(--rf);
                {'color:#48BB78;background:rgba(72,187,120,0.08);border:1px solid rgba(72,187,120,0.18);' if ready else 'color:#ED8936;background:rgba(237,137,54,0.08);border:1px solid rgba(237,137,54,0.18);'}
                font-family:'Inter',sans-serif;">
                {'Ready' if ready else 'No docs'}</span>
            </div>

            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span style="font-size:13.5px;color:var(--t2);font-family:'Inter',sans-serif;">Indexed Chunks</span>
              <span style="font-size:11px;font-weight:600;color:var(--v);
                background:rgba(124,92,252,0.06);padding:4px 14px;border-radius:var(--rf);
                border:1px solid rgba(124,92,252,0.10);
                font-family:'Inter',sans-serif;">{chunks}</span>
            </div>

            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span style="font-size:13.5px;color:var(--t2);font-family:'Inter',sans-serif;">Indexed Files</span>
              <span style="font-size:11px;font-weight:600;color:var(--v);
                background:rgba(124,92,252,0.06);padding:4px 14px;border-radius:var(--rf);
                border:1px solid rgba(124,92,252,0.10);
                font-family:'Inter',sans-serif;">{len(files)}</span>
            </div>

          </div>
        </div>

        <!-- MLOps Notes -->
        <div style="background:linear-gradient(135deg,#F6F2FF,#F0ECFE);
          border:1px solid rgba(124,92,252,0.10);border-radius:20px;
          padding:24px 28px;
          box-shadow:0 1px 4px rgba(45,43,85,0.03),0 4px 24px rgba(124,92,252,0.04);
          animation:slideUp 0.5s ease .4s both;">
          <div style="font-size:10px;font-weight:700;color:var(--v);
            letter-spacing:0.1em;text-transform:uppercase;margin-bottom:14px;
            font-family:'Inter',sans-serif;">MLOps Notes</div>
          <div style="font-size:13.5px;color:var(--t2);line-height:1.85;
            font-family:'Inter',sans-serif;">
            This observability layer tracks refusal rate and latency — the two key RAG quality KPIs.
            Refusal rate above 25% may indicate your threshold is too strict.
            Avg latency above 5s suggests a GPU upgrade or model swap to llama3.3:70b.
          </div>
          <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap;">
            <span style="font-size:10px;font-weight:600;color:var(--v);
              background:#FFFFFF;padding:4px 14px;border-radius:var(--rf);
              border:1px solid rgba(124,92,252,0.12);
              font-family:'Inter',sans-serif;">analytics.json</span>
            <span style="font-size:10px;font-weight:600;color:#38B2AC;
              background:rgba(56,178,172,0.06);padding:4px 14px;border-radius:var(--rf);
              border:1px solid rgba(56,178,172,0.15);
              font-family:'Inter',sans-serif;">200 query rolling window</span>
          </div>
        </div>

      </div>

    </div>""")
