"""Plotly chart builders. Plotly is imported inside each function so the rest of the
project (and the tests) work without it. Charts never rely on colour alone: they use
text labels, markers and axis titles."""


def _style(fig, title, height=340):
    fig.update_layout(title=title, template="plotly_white", height=height, margin=dict(l=20, r=20, t=60, b=40),
                      font=dict(size=14, color="#26283B"), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def mood_distribution_chart(dist):
    import plotly.graph_objects as go
    fig = go.Figure(go.Bar(x=dist["label"], y=dist["count"], text=dist["count"], textposition="outside",
                           marker_color="#8E86C9"))
    fig.update_yaxes(title="Number of check-ins", rangemode="tozero", dtick=1)
    fig.update_xaxes(title="Self-reported mood")
    return _style(fig, "Mood distribution")


def trend_chart(daily, column, title, y_title, y_range, color="#4A7FB5", symbol="circle"):
    import plotly.graph_objects as go
    fig = go.Figure(go.Scatter(x=daily["date"], y=daily[column], mode="lines+markers+text",
                               text=[f"{v:.1f}" for v in daily[column]], textposition="top center",
                               line=dict(color=color, width=3), marker=dict(size=9, symbol=symbol)))
    fig.update_yaxes(title=y_title, range=y_range)
    fig.update_xaxes(title="Date")
    return _style(fig, title)
