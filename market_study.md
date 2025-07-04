# Pricing Model for Django Glass Shop App (Algerian Freelance Rates)

Local Algerian freelancers charge very low fixed prices for web development. For context, a recent Twine survey notes that *“Beginner”* web projects in Algeria go for only **5,000–10,000 DZD** total.  Likewise, an Algerian web design firm quotes about **5,800–7,700 DZD per page** for a basic (static) site.  This suggests an entry-level freelancer might charge on the order of a few hundred to \~1,000 DZD per item (well below agency rates).  Accordingly, we assign unit costs at the low end of these norms: roughly **700–800 DZD** per HTML template or form, **800–1,000 DZD** per view or JS script, and about **1,500 DZD** per model class.  Multiplying by the counts from the project structure yields the table below (showing DZD and USD at 1 USD = 135 DZD).

| Asset Type        | Count | Unit Price (DZD / USD) |       Total (DZD / USD)      |
| ----------------- | :---: | :--------------------: | :--------------------------: |
| **HTML template** |   49  |   750 DZD (\~\$5.56)   |    36,750 DZD (\~\$272.22)   |
| **Django view**   |   49  |   800 DZD (\~\$5.93)   |    39,200 DZD (\~\$290.37)   |
| **Django model**  |   15  |  1,500 DZD (\~\$11.11) |    22,500 DZD (\~\$166.67)   |
| **Django form**   |   15  |   800 DZD (\~\$5.93)   |    12,000 DZD (\~\$88.89)    |
| **JS script**     |   4   |   900 DZD (\~\$6.67)   |     3,600 DZD (\~\$26.67)    |
| **Subtotal**      |   –   |            –           | **114,050 DZD (\~\$844.81)** |

The **total** for the full project is therefore about **114,050 DZD** (≈**\$845 USD**).  These estimates assume *entry-level* freelance rates in Algeria.  They are much lower than agency quotes, consistent with Twine’s observation that beginners often quote only \~5–10k DZD for an entire small project.  (Larger or more experienced freelancers would charge more per item.)

**Sources:** Local Algerian pricing data were used to guide these per-item estimates, ensuring the rates reflect the *low end* of the market. Each deliverable count comes from the glass shop project structure and was multiplied by the unit costs above to compute subtotals and the grand total.
