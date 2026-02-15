# SARView

![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green.svg) ![Version](https://img.shields.io/badge/version-0.1.0-blue) ![License](https://img.shields.io/badge/license-GPLv3-green)

**SARView** is a QGIS Python plugin for the rapid visualization of Synthetic Aperture Radar (SAR) data.

It addresses the high dynamic range inherent in SAR backscatter (linear intensity/amplitude) by computing a logarithmic transformation ($dB$) and applying a statistical histogram stretch in memory. This allows for immediate visual inspection of structures and backscatter distribution without generating permanent intermediate files.

## Methodology

SAR intensity data follows a Gamma distribution with a long tail, rendering standard linear min-max stretching ineffective for visualization. This tool implements the following processing chain:

**1. Logarithmic Scaling**
Converts linear data (DN) to Decibels ($dB$) to compress the dynamic range:
$$
\text{Value}_{dB} = k \cdot \log_{10}(\text{DN} + \epsilon)
$$
* **$k$**: Scaling factor ($10$ for Intensity/Power, $20$ for Amplitude).
* **$\epsilon$**: Bias term ($1\mathrm{e}{-5}$) to ensure numerical stability over zero-value pixels.

**2. Statistical Outlier Removal**
Applies a cumulative cut stretch based on the image statistics to mitigate speckle noise and outliers:
$$
\text{Range} = [\mu - n\sigma, \mu + n\sigma]
$$
* **$\mu$**: Mean of the log-transformed layer.
* **$\sigma$**: Standard deviation.
* **$n$**: Multiplier (typically $2.0$).

## Installation

### Prerequisites
* QGIS 3.22+
* Standard QGIS Python environment (PyQt5, numpy).

### Manual Installation
1.  Download the repository as a `.zip` file.
2.  Open QGIS.
3.  Navigate to **Plugins** > **Manage and Install Plugins** > **Install from ZIP**.
4.  Select the archive and install.

## Usage

1.  **Input Layer**: Select the target raster layer from the dropdown (must be loaded in the Project).
2.  **Parameters**:
    * **Log Factor ($k$)**: Set to `10.0` for Intensity products (e.g., Sentinel-1 GRD), or `20.0` for Amplitude.
    * **Sigma Multiplier ($n$)**: Defines the clipping range. A value of `2.0` is recommended for general inspection; lower values (`1.5`) increase contrast for low-backscatter features.
3.  **Processing**: Click **Enhance**. The tool generates a Virtual Raster (VRT) in memory.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss the proposed modification.

## License

This project is licensed under the GNU General Public License v3.0.

---
**Author:** Mohamad El Moussawi
**Contact:** mohamad.elmoussawi@mail.polimi.it