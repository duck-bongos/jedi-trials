
@if exist data\ (
	echo data directory exists. checking for data/annotated...

	if exist data\annotated (
		echo data\annotated directory exists. checking for data\annotated\source...

		if exist data\annotated\source (
			echo data\annotated\source exists. Cleaning...
			del /f /q data\annotated\source\*
			echo data\annotated\source is now empty.
		)

		if exist data\annotated\target (
			echo data\annotated\target exists. Cleaning...
			del /f /q data\annotated\target\*
			echo data\annotated\target is now empty.
		)
	)
)
