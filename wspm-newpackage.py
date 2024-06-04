import tkinter as tk

def submit():
    results = [textbox.get(1.0, 'end-1c') for textbox in textboxes]
    print("Results:", results)

# Create the main window
frame = tk.Tk()
frame.title("wspm create metadata")

# Create labels and textboxes using grid
labels = ["Name:", "Files:", "Version:", "OSes:", "Dependencies:"]
textboxes = []
for i in range(5):
    label = tk.Label(frame, text=labels[i])
    label.grid(row=i, column=0, padx=10, pady=5, sticky=tk.E)
    textbox = tk.Text(frame, width=30, height=1)
    textbox.grid(row=i, column=1, padx=5, pady=5)
    textboxes.append(textbox)

# Create submit button
submit_button = tk.Button(frame, text="Submit", command=submit)
submit_button.grid(row=5, columnspan=3, pady=12)

# Run the Tkinter event loop
frame.mainloop()
