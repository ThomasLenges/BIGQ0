from arduino.app_utils import App
import matplotlib
matplotlib.use('Agg')  # No screen to avoid docker crash
import matplotlib.pyplot as plt

# Crée un graphique simple
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [10, 20, 15, 30])
ax.set_title("Test matplotlib")
plt.savefig("/app/assets/test_plot.png")
plt.close()

print("Plot sauvegardé dans /assets/test_plot.png")

App.run()