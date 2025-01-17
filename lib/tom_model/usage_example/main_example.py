import declare_entire_model


if __name__ == '__main__':
    my_model = declare_entire_model.declare_model()     # Declare model
    for i in range(10):
        print('\nTime step {}'.format(i))               # Print information
        for var in my_model.get_all_variables(get_raw_data=False):
            var.print_variable()
        my_model.update_entire_model()                  # Update model
