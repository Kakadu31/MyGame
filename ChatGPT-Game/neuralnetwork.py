import numpy as np

# Define Neural Network Class
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        self.weights_input_hidden = np.random.randn(input_size, hidden_size)
        self.bias_hidden = np.zeros(hidden_size)
        self.weights_hidden_output = np.random.randn(hidden_size, output_size)
        self.bias_output = np.zeros(output_size)
    
    def feedforward(self, inputs):
        cleaned_inputs = np.nan_to_num(inputs, nan=0, posinf=9999, neginf=-9999)
        normalized_inputs = (cleaned_inputs - np.min(cleaned_inputs)) / (np.max(cleaned_inputs) - np.min(cleaned_inputs))
        hidden_layer = np.dot(normalized_inputs, self.weights_input_hidden) + self.bias_hidden
        hidden_layer_activation = 1 / (1 + np.exp(-hidden_layer))  # Sigmoid activation
        output_layer = np.dot(hidden_layer_activation, self.weights_hidden_output) + self.bias_output
        return output_layer