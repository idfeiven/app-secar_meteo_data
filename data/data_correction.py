'''
This module provides functions for correcting and cleaning data entries.
It includes functionalities for handling missing values, removing duplicates,
and standardizing data formats.

(c) 2025 Iván Domínguez Fuentes
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def calculate_error_metrics(df, col_true='daily_rain_pws_mm', col_est='daily_rain_gage_mm'):
    """
    Compara dos columnas cualesquiera de un DataFrame y calcula MAE, RMSE
    y error medio relativo (MAPE, en %) sobre los eventos con precipitación
    (al menos una de las dos columnas > 0).
    Además genera un scatter plot (variable independiente = col_true en x,
    variable dependiente = col_est en y) y dibuja la recta de ajuste del tipo
    y = a * x.
    """

    # Validación de columnas
    if col_true not in df.columns or col_est not in df.columns:
        raise ValueError(f"Columnas no encontradas en el DataFrame: {col_true}, {col_est}")

    # Quitamos filas con nulos en las dos columnas relevantes
    df = df.dropna(subset=[col_true, col_est]).copy()

    # Nos centramos en eventos de precipitación (al menos una de las medidas > 0)
    df = df[(df[col_true] > 0) | (df[col_est] > 0)]

    if df.empty:
        print('No hay datos de precipitación para comparar')
        return None

    # true := referencia, est := estimado
    true = df[col_true].to_numpy(dtype=float)
    est = df[col_est].to_numpy(dtype=float)
    err = true - est

    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err**2))

    # MAPE: calcular solo donde la referencia (true) > 0 para evitar división por cero
    mask = true > 0
    if mask.any():
        mape = np.mean(np.abs((true[mask] - est[mask]) / true[mask])) * 100.0
        mape_n = int(mask.sum())
    else:
        mape = np.nan
        mape_n = 0

    # --- Ajuste del tipo y = a * x (x = true, y = est) ---
    finite_mask = np.isfinite(true) & np.isfinite(est)
    a = np.nan
    r2 = np.nan
    if finite_mask.sum() > 0:
        x_fit = true[finite_mask]
        y_fit = est[finite_mask]
        denom = np.sum(x_fit * x_fit)
        if denom != 0:
            a = np.sum(x_fit * y_fit) / denom
            # R^2 de la regresión sin intercepto
            ss_tot = np.sum((y_fit - y_fit.mean())**2)
            ss_res = np.sum((y_fit - a * x_fit)**2)
            if ss_tot > 0:
                r2 = 1 - ss_res / ss_tot
            else:
                r2 = np.nan

    print(f'Columnas comparadas: {col_true} (referencia), {col_est} (estimada)')
    print(f'Analizados {len(df)} eventos de precipitación')
    print(f'MAE: {mae:.2f}')
    print(f'RMSE: {rmse:.2f}')
    if mape_n > 0:
        print(f'Error medio relativo (MAPE): {mape:.2f} % (calculado en {mape_n} eventos con referencia > 0)')
    else:
        print('MAPE no disponible: no hay eventos con referencia > 0')
    if not np.isnan(a):
        print(f'Ajuste sin intercepto: y = a * x, a = {a:.4f}, R² = {r2 if not np.isnan(r2) else "N/A"}')

    # --- Scatter plot: verdadero (x) vs estimado (y) con recta y = a*x ---
    plt.figure(figsize=(6, 6))
    plt.scatter(true, est, alpha=0.7, s=40, edgecolors='w', linewidth=0.5)
    finite_x = true[np.isfinite(true)]
    finite_y = est[np.isfinite(est)]
    if finite_x.size > 0 and finite_y.size > 0:
        lo = min(finite_x.min(), finite_y.min())
        hi = max(finite_x.max(), finite_y.max())
        if lo == hi:
            lo -= 1.0
            hi += 1.0
        pad = (hi - lo) * 0.05
        line_x = np.linspace(lo - pad, hi + pad, 100)
        if not np.isnan(a):
            line_y = a * line_x
            plt.plot(line_x, line_y, 'r--', label=f'y = {a:.3f} x (R²={r2:.2f})' if not np.isnan(r2) else f'y = {a:.3f} x')
        # dibujar también la línea y = x como referencia visual si procede
        plt.plot(line_x, line_x, 'k:', label='y = x')
        plt.xlim(lo - pad, hi + pad)
        plt.ylim(lo - pad, hi + pad)
    plt.xlabel(f'Verdadero (indep): {col_true}')
    plt.ylabel(f'Estimado (dep): {col_est}')
    mape_str = f"{mape:.2f}%" if not np.isnan(mape) else "N/A"
    plt.title(f'{col_true} vs {col_est}\nMAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape_str}')
    plt.grid(True, linestyle=':', linewidth=0.5)
    plt.legend()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.show()

    return {
        'col_true': col_true,
        'col_est': col_est,
        'mae': float(mae),
        'rmse': float(rmse),
        'mape_perc': (float(mape) if not np.isnan(mape) else None),
        'mape_n': mape_n,
        'n': int(len(df)),
        'fit_a': (float(a) if not np.isnan(a) else None),
        'fit_r2': (float(r2) if not np.isnan(r2) else None)
    }

def plot_mape_by_precip_intervals(daily_df, col_true='daily_rain_pws_mm', col_est='daily_rain_gage_mm'):
    """
    Calcula y representa el MAPE (%) por intervalos de precipitación tomando
    como referencia la columna `col_true` (por defecto 'daily_rain_mm').
    Intervalos: [0,5), [5,10), [10,20), >=20 (mm).
    Devuelve un DataFrame con MAPE y número de eventos por intervalo.
    """
    if col_true not in daily_df.columns:
        raise ValueError(f"Columna verdadera no encontrada: {col_true}")
    if col_est not in daily_df.columns:
        raise ValueError(f"Columna estimada no encontrada: {col_est}")

    df = daily_df.copy()
    # eliminar filas sin datos esenciales
    df = df.dropna(subset=[col_true, col_est]).copy()
    # considerar solo eventos con referencia > 0 (necesario para MAPE)
    df = df[df[col_true] > 0]

    bins = [0, 5, 10, 20, np.inf]
    labels = ['[0,5)', '[5,10)', '[10,20)', '>=20']
    df['pcp_bin'] = pd.cut(df[col_true], bins=bins, right=False, labels=labels)

    def compute_mape(t, e):
        mask = t > 0
        if mask.sum() == 0:
            return np.nan, 0
        mape = np.mean(np.abs((t[mask] - e[mask]) / t[mask])) * 100.0
        return mape, int(mask.sum())

    results = []
    for lab in labels:
        g = df[df['pcp_bin'] == lab]
        if g.empty:
            results.append({'interval': lab, 'mape_perc': np.nan, 'n': 0})
        else:
            mape, n = compute_mape(g[col_true].to_numpy(dtype=float),
                                   g[col_est].to_numpy(dtype=float))
            results.append({'interval': lab, 'mape_perc': (float(mape) if not np.isnan(mape) else np.nan), 'n': n})

    res_df = pd.DataFrame(results).set_index('interval')

    # Plot de barras
    plt.figure(figsize=(10, 6))
    bars = plt.bar(res_df.index, res_df['mape_perc'].fillna(0), color='C0', edgecolor='k', alpha=0.85)
    plt.ylabel('MAPE (%)')
    plt.xlabel('Intervalos de precipitación (mm)')
    plt.title(f'MAPE por intervalo ({col_true} como referencia)')
    plt.grid(axis='y', linestyle=':', linewidth=0.5)

    # Anotar conteos y valor numérico del MAPE
    for bar, (_, row) in zip(bars, res_df.iterrows()):
        h = bar.get_height()
        mape_val = row['mape_perc']
        n_val = int(row['n'])

        # Texto para MAPE: mostrar "N/A" si no hay valor
        if np.isnan(mape_val):
            mape_text = "MAPE: N/A"
        else:
            mape_text = f"MAPE: {mape_val:.1f}%"

        # Para intervalos sin eventos, atenuar barra y anotar en la base
        if n_val == 0:
            bar.set_alpha(0.3)
            plt.text(bar.get_x() + bar.get_width()/2, 0.5, 'n=0', ha='center', va='bottom', fontsize=9, color='red')
            plt.text(bar.get_x() + bar.get_width()/2, 1.2, 'MAPE: N/A', ha='center', va='bottom', fontsize=9, color='red')
        else:
            # colocar MAPE y n por encima de la barra
            offset_mape = max(0.5, 0.02 * h)
            offset_n = offset_mape + 0.9
            plt.text(bar.get_x() + bar.get_width()/2, h + offset_mape, mape_text, ha='center', va='bottom', fontsize=9)
            plt.text(bar.get_x() + bar.get_width()/2, h + offset_n, f"n={n_val}", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()

    return res_df


daily_data = pd.read_excel("secar_daily_data.xlsx")
daily_data = daily_data.drop(columns=['Unnamed: 0'])

print('Analizando datos de precipitación diarios')
err_metrics = calculate_error_metrics(daily_data, col_true='daily_rain_gage_mm', col_est='daily_rain_pws_mm')

print('Representando MAPE por intervalos de precipitación')
res_df = plot_mape_by_precip_intervals(daily_data)

df_1 = daily_data[(daily_data['daily_rain_gage_mm']>0) & (daily_data['date']<'2021-02-06')]
df_1_1 = df_1[df_1['correction'] != 1]
df_1_1['daily_rain_mm_corr'] = err_metrics['fit_a']*df_1_1['daily_rain_gage_mm']
df_1_2 = df_1[df_1['correction'] == 1]
df_1_2['daily_rain_mm_corr'] = df_1_2['daily_rain_gage_mm']
df_1 = pd.concat([df_1_1, df_1_2])
df_1['daily_rain_mm_corr'] = df_1['daily_rain_mm_corr'].round(1)

df_2 = daily_data[(daily_data['daily_rain_gage_mm']>0) & (daily_data['date']>='2021-02-06')]
df_2_1 = df_2[df_2['correction'] != 1]
df_2_1['daily_rain_mm_corr'] = df_2_1['daily_rain_pws_mm']
df_2_2 = df_2[df_2['correction'] == 1]
df_2_2['daily_rain_mm_corr'] = df_2_2['daily_rain_gage_mm']
df_2 = pd.concat([df_2_1, df_2_2])

df = pd.concat([df_1, df_2])
df = df.sort_values(by='date')

daily_data_corr = df.merge(daily_data, how='right')
daily_data_corr['daily_rain_mm_corr'] = daily_data_corr['daily_rain_mm_corr'].fillna(0.0)
daily_data_corr.to_excel("secar_daily_data_corrected.xlsx", index=False)