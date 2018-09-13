import numpy as np
import matplotlib.pyplot as plt

def main():

    print('Finished!')

def Load_Text_Data(file_path='../goblet_book.txt'):
    """
    Reads the input data.

    :param file_path: (Optional) Position of the txt file in the local system.

    :return: book_data: all input characters and unique_characters: unique single characters of the input data.
    """
    book_data = open(file_path, 'r').read()
    unique_characters = list(set(book_data))

    return book_data, unique_characters

def Char_to_Ind(chars_list, unique_chars):
    """
    Maps the original characters to integers.

    :param chars_list: The list of characters to be encoded into integers.
    :param unique_chars: The set of unique characters available.

    :return: A list of integers that correspond to the characters.
    """

    encoded_characters = []

    for char in chars_list:
        for index, letter in enumerate(unique_chars):

            if char == letter:

                encoded_characters.append(index)

    return encoded_characters

def Ind_to_Char(one_hot_representation, unique_chars_list):
    """
    Maps a list of integers to their corresponding characters,

    :param one_hot_representation: A list of one_hot representations to be transformed to their correspoding characters.
    :param unique_chars_list: The list of unique characters.

    :return: The actual character sequence.
    """

    actual_character_sequence = []

    for i in range(one_hot_representation.shape[1]):

        letter_pos = np.where(one_hot_representation[:,i] == 1.0)[0][0]
        actual_character_sequence.append(unique_chars_list[letter_pos])

    return actual_character_sequence


def softmax(X, theta=1.0, axis=None):
    """
    Softmax over numpy rows and columns, taking care for overflow cases
    Many thanks to https://nolanbconaway.github.io/blog/2017/softmax-numpy
    Usage: Softmax over rows-> axis =0, softmax over columns ->axis =1

    :param X: ND-Array. Probably should be floats.
    :param theta: float parameter, used as a multiplier prior to exponentiation. Default = 1.0
    :param axis (optional): axis to compute values along. Default is the first non-singleton axis.

    :return: An array the same size as X. The result will sum to 1 along the specified axis
    """

    # make X at least 2d
    y = np.atleast_2d(X)

    # find axis
    if axis is None:
        axis = next(j[0] for j in enumerate(y.shape) if j[1] > 1)
    # multiply y against the theta parameter,
    y = y * float(theta)

    # subtract the max for numerical stability
    y = y - np.expand_dims(np.max(y, axis=axis), axis)

    # exponentiate y
    y = np.exp(y)

    # take the sum along the specified axis
    ax_sum = np.expand_dims(np.sum(y, axis=axis), axis)

    # finally: divide elementwise
    p = y / ax_sum

    # flatten if X was 1D
    if len(X.shape) == 1: p = p.flatten()

    return p

def create_one_hot_endoding(x, K):
    """
    Creates the one hot encoding representation of an array.


    :param x: The array that we wish to map in an one-hot representation.
    :param K: The number of distinct classes.

    :return: One hot representation of this number.
    """

    x_encoded = np.zeros((K, len(x)))
    for index, elem in enumerate(x):

        x_encoded[elem, index] = 1.0

    return x_encoded

class RNN:
    """
    Recurrent Neural Network object
    """

    def __init__(self, m, K, eta, seq_length, std):
        """
        Initial setting of the RNN.

        :param m: Dimensionality of the hidden state.
        :param K: Number of unique classes to identify.
        :param eta: The learning rate of the training process.
        :param seq_length: The length of the input sequence.
        :param std: the variance of the normal distribution that initializes the weight matrices.
        """

        self.m = m
        self.K = K
        self.eta = eta
        self.seq_length = seq_length
        self.std = std

    def init_weights(self):
        """
        Initializes the weights and bias matrices
        """

        U = np.random.randn(self.m, self.K) * self.std
        W = np.random.randn(self.m, self.m) * self.std
        V = np.random.randn(self.K, self.m) * self.std

        b = np.zeros((self.m, 1))
        c = np.zeros((self.K, 1))

        return W, U, b, V, c

    def synthesize_sequence(self, h0, x0, W, U, b, V, c, seq_length):
        """
        Synthesizes a sequence of characters under the RNN values.

        :param self: The RNN.
        :param h0: Hidden state at time 0.
        :param x0: First (dummy) input vector of the RNN.
        :param W: Hidden-to-Hidden weight matrix.
        :param U: Input-to-Hidden weight matrix.
        :param b: Bias vector of the hidden layer.
        :param V: Hidden-to-Output weight matrix.
        :param c: Bias vector of the output layer.
        :param seq_length: Length of the sequence that we wish to generate.


        :return: Synthesized text through.
        """
        Y = np.zeros(x0.shape)

        alpha = np.dot(W, h0) + np.dot(U, np.expand_dims(x0[:,0], axis=1)) + b
        h = np.tanh(alpha)
        o = np.dot(V, h) + c
        p = softmax(o)

        # Compute the cumulative sum of p and draw a random sample from [0,1)
        cumulative_sum = np.cumsum(p)
        draw_number = np.random.sample()

        # Find the element that corresponds to this random sample
        pos = np.where(cumulative_sum > draw_number)[0][0]

        # Create one-hot representation of the found position
        Y[pos, 0] = 1.0

        h0 = np.copy(h)
        x0 = np.expand_dims(np.copy(Y[:,0]), axis=1)

        for index in range(1, seq_length):

            alpha = np.dot(W, h0) + np.dot(U, x0) + b
            h = np.tanh(alpha)
            o = np.dot(V, h) + c
            p = softmax(o)

            # Compute the cumulative sum of p and draw a random sample from [0,1)
            cumulative_sum = np.cumsum(p)
            draw_number = np.random.sample()

            # Find the element that corresponds to this random sample
            pos = np.where(cumulative_sum > draw_number)[0][0]

            # Create one-hot representation of the found position
            Y[pos, index] = 1.0

            h0 = np.copy(h)
            x0 = np.expand_dims(np.copy(Y[:, index]), axis=1)

        return Y

    def ComputeLoss(self, input_sequence, Y, weight_parameters):
        """
        Computes the cross-entropy loss of the RNN.

        :param input_sequence: The input sequence.
        :param weight_parameters: Weights and matrices of the RNN, which in particularly are:
            :param W: Hidden-to-Hidden weight matrix.
            :param U: Input-to-Hidden weight matrix.
            :param b: Bias vector of the hidden layer.
            :param V: Hidden-to-Output weight matrix.
            :param c: Bias vector of the output layer.

        :return: Cross entropy loss (divergence between the predictions and the true output)
        """
        W, U, b, V, c = weight_parameters

        p = self.ForwardPass(input_sequence, W, U, b, V, c)[2]
        cross_entropy_loss = -np.log(np.diag(np.dot(Y.T, p))).sum() / float(input_sequence.shape[1])

        return cross_entropy_loss

    def ForwardPass(self, input_sequence, weight_parameters):
        """
        Evaluates the predictions that the RNN does in an input character sequence.

        :param input_sequence: The one-hot representation of the input sequence.
        :param weight_parameters: The weights and biases of the network, which are:
            :param W: Hidden-to-Hidden weight matrix.
            :param U: Input-to-Hidden weight matrix.
            :param b: Bias vector of the hidden layer.
            :param V: Hidden-to-Output weight matrix.
            :param c: Bias vector of the output layer.

        :return: The predicted character sequence based on the input one.
        """

        W, U, b, V, c = weight_parameters

        p = np.zeros(input_sequence.shape)
        h_list = [np.zeros((self.m, 1))]
        a_list = []

        for index in range(0, input_sequence.shape[1]):

            alpha = np.dot(W, h[-1]) + np.dot(U, np.expand_dims(input_sequence[:,index], axis=1)) + b
            a_list.append(alpha)
            h = np.tanh(alpha)
            h_list.append(h)
            o = np.dot(V, h) + c
            p = softmax(o)

            # Compute the cumulative sum of p and draw a random sample from [0,1)
            cumulative_sum = np.cumsum(p)
            draw_number = np.random.sample()

            # Find the element that corresponds to this random sample
            pos = np.where(cumulative_sum > draw_number)[0][0]

            # Create one-hot representation of the found position
            p[pos, index] = 1.0

        return a_list, h, p

    def BackwardPass(self, x, Y, p, W, V, a, h):
        """
        Computes the gradient updates of the network's weight and bias matrices based on the divergence between the
        prediction and the true output.

        :param x: Input data to the network.
        :param p: Predictions of the network.
        :param Y: One-hot representation of the correct sequence.
        :param W: Hidden-to-Hidden weight matrix.
        :param V: Hidden-to-Output weight matrix.
        :param a: TODO
        :param h: Hidden states of the network at each time step.

        :return:  Gradient updates.
        """

        # grad_W, grad_U, grad_b, grad_V, grad_c = \
        #     np.zeros(W.shape), np.zeros((W.shape[0], x.shape[1])), np.zeros((W.shape[0], 1)), np.zeros(V), np.zeros((x.shape[0], 1))

        # Computing the gradients for the last time step

        grad_c = np.expand_dims((p[:, x.shape[1]- 1] - Y[:, x.shape[1]- 1]).T, axis=1)
        grad_V = np.dot(grad_c, h[x.shape[1]- 1].Τ)

        grad_h = np.dot(grad_c, V)

        grad_b = np.dot(grad_h, np.diag(1 - a[x.shape[1] -1 ]**2))

        grad_W = np.dot(grad_b.T, h[x.shape[1] - 2].T)
        grad_U = np.dot(grad_b.T, x[:,x.shape[1]-1].T)

        grad_a = grad_b

        for time_step in reversed(range(x.shape[1]- 1)):

            grad_o = np.expand_dims((p[:, time_step] - Y[:, time_step]).T, axis=1)
            grad_V += np.dot(grad_o, h[x.shape[1] - 1].Τ)
            grad_c += grad_o

            grad_h = np.dot(grad_c, V) + np.dot(grad_a, W)

            grad_a = np.dot(grad_h, np.diag(1 - a[time_step] ** 2))

            grad_W += np.dot(grad_a.T, h[x.shape[1] - 2].T)
            grad_U += np.dot(grad_a.T, x[:, x.shape[1] - 1].T)

            grad_b += grad_a

        return [grad_W, grad_U, grad_b, grad_V, grad_c]

class Gradients:

    def __init__(self, RNN):
        self.RNN = RNN

    def ComputeGradients(self, X, Y, weight_parameters):
        """
        Computes the analytical gradient updates of the network.
        :param X: Input sequence.
        :param Y: True output
        :param weight_parameters: Weights and bias matrices of the network.

        :return: Gradients updates.
        """

        a_list, h_list, p = RNN.ForwardPass(X, weight_parameters)
        gradients = RNN.BackwardPass(X, Y, p, weight_parameters[0], weight_parameters[3], a_list, h_list)

        return gradients

    def ComputeGradsNumSlow(self, X, Y, h=1e-4):

        W, U, b, V, c = RNN.init_weights()
        all_weights = [W, U, b, V, c]

        all_grads_num = []

        for index, elem in all_weights:

            grad_elem = np.zeros(elem.shape)
            # h_prev = np.zeros((W.shape[1], 1))

            for i in range(elem.shape[0]):
                for j in range(elem.shape[1]):

                    elem_try = np.copy(elem)
                    elem_try[i, j] -= h
                    all_weights_try = np.copy(all_weights)
                    all_weights_try[index] = elem_try
                    c1 = RNN.ComputeLoss(X, Y, weight_parameters=all_weights_try)

                    elem_try = np.copy(elem)
                    elem_try[i, j] += h
                    all_weights_try = np.copy(all_weights)
                    all_weights_try[index] = elem_try
                    c2 = RNN.ComputeLoss(X, Y, weight_parameters=all_weights_try)

                    grad_elem[i, j] = (c2-c1) / h

            all_grads_num.append(grad_elem)

    def check_similarity(self, X, Y, weight_parameters):
        """
        Computes and compares the analytical and numerical gradients.

        :param X: Input sequence.
        :param Y: True output
        :param weight_parameters: Weights and bias matrices of the network.

        :return: None.
        """
        analytical_gradiens = self.ComputeGradients(X, Y, weight_parameters)
        numerical_gradiens = self.ComputeGradsNumSlow(X, Y, weight_parameters)

        for weight_index in range(len(analytical_gradiens)):
            print('-----------------')
            print(f'Weight parameter no. {weight_index+1}:')

            weight_abs = np.abs(analytical_gradiens[weight_index] - numerical_gradiens[weight_index])

            weight_nominator = np.average(weight_abs)

            grad_weight_abs = np.absolute(analytical_gradiens[weight_index])
            grad_weight_num_abs = np.absolute(numerical_gradiens[weight_index])

            sum_weight = grad_weight_abs + grad_weight_num_abs

            print(f'Deviation between analytical and numerical gradients: {weight_nominator / np.amax(sum_weight)}')

def main():

    book_data, unique_characters = Load_Text_Data()

    rnn = RNN(m=100, K=len(unique_characters), eta=0.1, seq_length=25, std=0.1)

    W, U, b, V, c = rnn.init_weights()

    input_sequence = book_data[:rnn.seq_length]

    integer_encoding = Char_to_Ind(input_sequence, unique_characters)
    input_sequence_one_hot = create_one_hot_endoding(integer_encoding, len(unique_characters))

    test = rnn.ForwardPass(input_sequence_one_hot, W, U, b, V, c)
    test2 = Ind_to_Char(test, unique_characters)
    print(''.join(test2))
    print('Finished!')

if __name__=='__main__':
    main()




