(use-modules ((guix licenses)
              #:prefix license:)
             (guix packages)
             (guix download)
             (guix build-system python)
             (guix build-system pyproject)
             (gnu packages time)
             (gnu packages python-xyz)
             (guix git-download)
             (gnu packages python-check)
             (gnu packages python-web)
             (gnu packages certs)
             (gnu packages databases)
             (gnu packages check)
             (gnu packages python-build))

(define-public python-ics
  (package
    (name "python-ics")
    (version "0.7.2")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "ics" version))
       (sha256
        (base32 "01cz428xy8bmgjzvx610p0haz50hrm7xg1wv4hsicf8hradm6hv7"))))
    (build-system pyproject-build-system)
    (arguments
     (list
      #:tests? #f)) ;TODO: enable
    (propagated-inputs (list python-arrow python-attrs python-dateutil
                             python-six python-tatsu))
    (native-inputs (list python-setuptools
                         python-wheel
                         python-pip
                         python-mypy
                         python-pytest-sugar
                         python-freezegun))
    (home-page "http://github.com/C4ptainCrunch/ics.py")
    (synopsis "Python icalendar (rfc5545) parser")
    (description "Python icalendar (rfc5545) parser.")
    (license license:asl2.0)))

(concatenate-manifests
 (list (specifications->manifest (list "python@3.10" ;https://docs.python.org/ja/3.10/
                                       "python-aiohttp"
                                       "python-dotenv"
                                       "poetry"
                                       "python-sphinx"
                                       "python-myst-parser"
                                       "python-sphinx-intl"
                                       "python-mypy"
                                       "python-aiohttp-client-cache"))
       (packages->manifest (list python-ics
                                 python-isodate))))
