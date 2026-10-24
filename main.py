/* FIX 1: Cards no cut-off - from 220px min-height + flex */
.cards{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:16px}
.card{background:#ffffff;border-radius:24px;padding:20px 16px;text-align:center;border:1px solid #e2e8f0;box-shadow:0 12px 32px rgba(0,0,0,0.12);display:flex;flex-direction:column;min-height:240px}
.card-desc{flex-grow:1;line-height:1.6}

/* FIX 2: How It Works readable - dark text on white */
.how-container{background:#ffffff;border-radius:24px;padding:22px;border:1px solid #e2e8f0}
.how-card{background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:20px;padding:18px;display:flex;gap:14px}
.how-card-title{font-size:13px;font-weight:800;color:#0f172a}
.how-card-text{font-size:11px;color:#475569;line-height:1.7}

/* FIX 3: Bottom nav NOT covering - padding-bottom 150px */
.phone{max-width:430px;margin:0 auto;min-height:100vh;padding-bottom:150px;overflow-x:hidden}
.nav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);max-width:430px;width:100%;padding:12px 0 20px;z-index:100}

/* FIX 4: Inputs readable - label 10px uppercase + margin */
.field{margin-top:16px}
.label{font-size:10px;font-weight:800;text-transform:uppercase;color:#94a3b8;margin-bottom:8px;display:block}
.input{width:100%;padding:14px 16px;border-radius:12px;font-size:13px}
