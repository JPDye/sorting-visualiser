import src.visualise.algorithms as algos

from src.visualise.utilities import progress_bar, progress_complete

from PIL import Image
import numpy as np

class SortingVisualiser:
    def __init__(self, image, randomise=True, reverse=False):
        self.original = np.asarray(image, dtype="uint8")            # Save original image
        self.rows, self.columns, _ = self.original.shape
        self.replaced, self.replace_dict = self.__replace_with_integers() # Replace pixels with consecutive integers for sorting

        if randomise:
            self.__randomise_image()
        if reverse:
            self.__reverse_image()

        self.swaps = []
        self.max_swaps = 0
        self.sorting_methods = {
            "bubble_sort": algos.bubble_sort,
            "cocktail_sort": algos.cocktail_sort,
            "selection_sort": algos.selection_sort,
            "insertion_sort": algos.insertion_sort,
            "quick_sort": algos.quick_sort,
            "heap_sort": algos.heap_sort,
            "merge_sort": algos.it_merge_sort,
            "radix_sort_lsd": algos.radix_sort_lsd,
            "counting_sort": algos.counting_sort,
            "my_sort": algos.my_sort
        }

    def __replace_with_integers(self):
        """
        Replaces pixels of image with consecutive integers. Creates dictionary for reverting to normal.
        """
        replaced = np.zeros((self.rows, self.columns))
        replace_dict = []

        for i in range(self.rows):
            temp_dict = {}
            for j in range(self.columns):
                temp_dict[j] = self.original[i, j]
                replaced[i, j] = j
            replace_dict.append(temp_dict)

        return replaced, replace_dict

    def _replace_with_pixels(self):
        """
        Use the replace_dict to convert image_array from consecutive integers back to their original
        pixel values.
        """
        pixel_array = np.zeros((self.rows, self.columns, 3), dtype="uint8")

        for row in range(self.rows):
            for column in range(self.columns):
                key = int(self.replaced[row, column])
                pixel = self.replace_dict[row][key]
                pixel_array[row, column] = pixel
        return pixel_array

    def __reverse_image(self):
        self.replaced = np.flip(self.replaced)

    def __randomise_image(self):
        for i in range(self.rows):
            np.random.shuffle(self.replaced[i, :])

    def __swap_pixels(self, row, start, end):          # Swap pixels for an in place algorithms
        for i, j in self.swaps[row][start:end]:
            self.replaced[row, i], self.replaced[row, j] = self.replaced[row, j], self.replaced[row, i]

    def sort(self, sorting_method):
        for row_index in range(self.rows):
            row = self.replaced[row_index, :].copy()
            temp_swaps = self.sorting_methods[sorting_method](row)
            self.swaps.append(temp_swaps)
            self.max_swaps = max(len(self.swaps[-1]), self.max_swaps)
            progress_bar("Sorting GIF:\t", row_index, self.rows)
        progress_complete("Sorting GIF:\t")

    def visualise(self, num_frames, sort_method="bubble_sort"):
        """
        Use the data in self.swaps to show the sorting process. The number of frames determines
        how much data from self.swaps is used to modify the image array per frame. More frames means
        smaller chunks which results in a smoother final result.

        There are two visualisation methods. Method one is for when an in-place sorting algorithm
        was used. Method two is for when an out-of-place soritng algorithm was used.

        An in-place algorithm will result in self.swaps being filled with the actual swaps made
        to move pixels into the correct position. In this case we simply replicate these swaps
        to show what happened when sorting the image. Swaps are captured as tuples of
        (pixel_1_pos, pixel_2_pos). We use this type checking to determine which algorithm was
        used.

        An out-of-place algorithm will result in self.swaps containg copies of the array taken
        after each pass. To visualise this we simply slowly replace the current array with elements
        from the snapshot of the array.
        """
        if not self.swaps:
            self.sort(sort_method)

        num_frames -= 1
        frames = [self._replace_with_pixels()]
        # Determine if an in-place sorting algorithm was used
        if type(self.swaps[0][0]) is tuple:
            swap_num = 0
            swap_step = self.max_swaps // num_frames    # Index needs to be an integer
            remainder = self.max_swaps % num_frames     # Find remainder from the int-division

            while swap_num <= self.max_swaps:
                if remainder > 0:       # Check if remainder is left over. Add 1 to index if there is.
                    remainder -= 1
                    extra = 1
                else:
                    extra = 0

                for row in range(self.rows):
                    self.__swap_pixels(row, swap_num, swap_num+swap_step+extra)
                swap_num += swap_step + extra
                frames.append(self._replace_with_pixels())
                progress_bar("Creating GIF:\t", swap_num / self.max_swaps, self.max_swaps)
            progress_complete("Creating GIF:\t")
        else:
            pos = 0
            swap_num = 0
            swap_step = int(self.max_swaps / num_frames)  # Round as index needs to be an integer
            remainder = self.max_swaps % num_frames         # Calculate amount lost from rounding

            while swap_num < self.max_swaps:
                if remainder > 0:       # Check if remainder is left over. Add 1 to index if there is.
                    remainder -= 1
                    extra = 1
                else:
                    extra = 0

                # Calculate end positions for swapping
                swap_end = swap_num + swap_step + extra
                pos_end = len(self.swaps[0][swap_num:swap_end]) # Use length of swap list to find end index.
                pos_end = (pos + pos_end) % self.columns        # If index is greater than length of list. Wrap it around.

                for row in range(self.rows):
                    if pos_end < pos:                           # Check if the index wrapped around
                        swap_amount = self.columns - pos
                        self.replaced[row, pos:] = self.swaps[row][swap_num:swap_num+swap_amount]       # Swap until end of list
                        self.replaced[row, :pos_end] = self.swaps[row][swap_num+swap_amount:swap_end]   # Swap from front to end index
                    else:
                        self.replaced[row, pos:pos_end] = self.swaps[row][swap_num:swap_end]
                swap_num += swap_step + extra
                pos = pos_end
                frames.append(self._replace_with_pixels())
                progress_bar("Creating GIF:\t", swap_num, self.max_swaps)
            progress_complete("Creating GIF:\t")
        return frames


